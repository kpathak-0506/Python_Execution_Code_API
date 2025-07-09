# Python Code Execution API

Welcome!
This is a mighty Flask API that safely runs Python code sent via HTTP. It’s built for experimentation and sandboxing, perfect for learning, testing, or running student-submitted code in a safe container.

I used **nsjail** for isolation, and Docker to make everything portable and deployment-ready.

# What This API Does

- Accepts a 'POST' request with a Python script
- Runs the script in a sandboxed environment using 'nsjail'
- Expects a 'main()' function and **only** returns what it returns
- Ignores all other print statements or side effects
- Prevents large or malicious scripts with size and type checks

# Requirements

- Docker
- Google Cloud SDK


# Run Locally (in Docker)

Build it:


code - docker build -t python-exec-api .

Then run it

code - docker run --privileged -p 8080:8080 python-exec-api


That’s it. The API should now be live on https://python-exec-api-290803380630.us-west1.run.app/

Testing with curl
1) Valid Script

curl -X POST https://python-exec-api-290803380630.us-west1.run.app/execute
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n return {\"msg\": \"hello\"}"}'
Expected output:

{ "result": { "msg": "hello" } }

2) Invalid Script (Number Instead of String)

curl -X POST https://python-exec-api-290803380630.us-west1.run.app/execute
  -H "Content-Type: application/json" \
  -d '{"script": 12345}'
Expected output:

{ "error": "'script' must be a string and included in the request" }

3) Missing 'script' Field

curl -X POST https://python-exec-api-290803380630.us-west1.run.app/execute
  -H "Content-Type: application/json" \
  -d '{"not_script": "print(\"oops\")"}'
Expected output:

{ "error": "'script' must be a string and included in the request" }

4) Script Too Big

curl -X POST https://python-exec-api-290803380630.us-west1.run.app/execute
  -H "Content-Type: application/json" \
  -d "{\"script\": \"$(head -c 11000 < /dev/zero | tr '\0' 'a')\"}"
Expected output:

{ "error": "Script too large. Max size allowed is 10KB." }



# Important Notes on nsjail
Initially, I tried to sandbox Python code execution using nsjail for enhanced security.

nsjail works perfectly when running locally ( in your Docker container on machine).

However, on Google Cloud Run, nsjail runs into low-level Linux kernel restrictions causing failures (errors with prctl and clone flags).

Because Cloud Run is a managed environment with limited kernel capabilities, nsjail’s sandboxing cannot function properly there.

To work around this, I temporarily switched to running user scripts safely using subprocess with time and memory limits.


# Running with nsjail(Local)
nsjail_cmd = [
    'nsjail',
    '--mode', 'o',
    '--time_limit', '3',
    '--rlimit_as', '500',
    '--disable_clone_newnet',
    '--disable_clone_newuser',
    '--disable_clone_newns',
   '--disable_clone_newpid',
    '--disable_clone_newipc',
    '--disable_clone_newuts',
    '--disable_clone_newcgroup',
   '--bindmount_ro', '/app',
   '--bindmount_ro', '/usr',
    '--bindmount_ro', '/usr/local/bin',
    '--bindmount_ro', '/lib',
   '--bindmount_ro', '/lib64',
   '--bindmount_ro', '/bin',
   '--bindmount_ro', temp_dir,   
   '--', '/usr/local/bin/python3', w_file_path
]


# With nsjail locally
![test1](https://github.com/user-attachments/assets/4900d42c-2bf3-476c-a4b6-866c9c5b6ea4)


![test2](https://github.com/user-attachments/assets/62d9c99c-e447-4673-bfac-3cb135ff0692)


![test3](https://github.com/user-attachments/assets/6cf195b6-7df6-4750-960e-67c34bd83375)


# Running with subprocess(Cloud Run)
 completed = subprocess.run(
            ['python3', w_file_path],
            capture_output=True,
            text=True,
            timeout=3
        )
# On Google cloud run
![test4](https://github.com/user-attachments/assets/f2a1943a-aa91-4a12-9a0c-d35bb84154dc)


