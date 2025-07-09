from flask import Flask, jsonify, request
import tempfile
import os
import json
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG)


app=Flask(__name__)

@app.route('/execute',methods=['POST'])

#------------------------------------------------Checking the incoming data-----------------------------------------------------

def run_script():
    data=request.get_json()
    print("Received data:", data)

    
    if not data or 'script' not in data or not isinstance(data['script'], str):
        return jsonify({"error": "'script' must be a string and included in the request"}), 400

    main_script = data['script']

    if len(main_script.encode('utf-8')) > 10 * 1024:
        return jsonify({"error": "Script too large. Max size allowed is 10KB."}), 413


    TEMP_DIR = '/tmp/nsjail-temp'

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR, exist_ok=True)
    
    print(f"type(main_script) before writing: {type(main_script)}")

    with tempfile.NamedTemporaryFile(mode='w',delete=False, suffix=".py",dir=TEMP_DIR) as file:
        file.write(main_script)
        main_script_path = file.name
    
#---------------------------------------------Wrapper code for running the python script------------------------------------------------
    w_code=f"""
import json
import sys
import importlib.util

spec = importlib.util.spec_from_file_location('main_script', r"{main_script_path}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

if not hasattr(module, 'main'):
    print(json.dumps({{"error": "No main() function found"}}))
    sys.exit(1)

result = module.main()

try:
    json_result = json.dumps(result)
except Exception:
    print(json.dumps({{"error": "main() did not return JSON serializable result"}}))
    sys.exit(1)

print(json_result)
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=TEMP_DIR) as w_file:
        w_file.write(w_code)
        w_file_path = w_file.name

    temp_dir = TEMP_DIR 

    try:
        completed = subprocess.run(
            ['python3', w_file_path],
            capture_output=True,
            text=True,
            timeout=3
        )

    except subprocess.TimeoutExpired:
        os.remove(main_script_path)
        os.remove(w_file_path)
        return jsonify({"error": "Execution timed out"}), 408
    except Exception as e:
        
        os.remove(main_script_path)
        os.remove(w_file_path)
        return jsonify({"error": "Execution failed", "exception": str(e)}), 500

  
    os.remove(main_script_path)
    os.remove(w_file_path)

    print("NSJail stdout:", completed.stdout)
    print("NSJail stderr:", completed.stderr)

    if completed.returncode != 0:
        error_details = {
             "returncode": completed.returncode,
             "stdout": completed.stdout.strip(),
             "stderr": completed.stderr.strip()
    }
        return jsonify({"error": "Execution failed", "details": error_details}), 400
    

    try:
        output_lines = [line for line in completed.stdout.strip().splitlines() if line.strip()]
        if not output_lines:
            return jsonify({"error": "No output from script"}), 400
        json_line = output_lines[-1]
        result_json = json.loads(json_line)
    except Exception as e:
        return jsonify({
        "error": "Failed to parse script output as JSON",
        "output": completed.stdout,
        "exception": str(e)
    }), 400

    return jsonify({
       "result": result_json,
       "stdout": completed.stderr 
})


if __name__=='__main__':
    app.run(host='0.0.0.0',port=8080)
    

