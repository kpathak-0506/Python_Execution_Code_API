# Python Code Execution API

Welcome!
This is a mighty Flask API that safely runs Python code sent via HTTP. It’s built for experimentation and sandboxing, perfect for learning, testing, or running student-submitted code in a safe container.

I used **nsjail** for isolation, and Docker to make everything portable and deployment-ready.

# What This API Does

- Accepts a `POST` request with a Python script
- Runs the script in a sandboxed environment using `nsjail`
- Expects a `main()` function and **only** returns what it returns
- Ignores all other print statements or side effects
- Prevents large or malicious scripts with size and type checks

# Requirements

- Docker
- Google Cloud SDK


# Run Locally (in Docker)

Build it:

```bash
code - docker build -t python-exec-api .

Then run it

code - docker run --privileged -p 8080:8080 python-exec-api


That’s it. The API should now be live on http://localhost:8080.

Testing (PowerShell)
1) Valid Script

$body = @{
    script = "def main():`n    return {'msg': 'hello'}"
} | ConvertTo-Json -Compress

Invoke-RestMethod -Method POST -Uri http://localhost:8080/execute -ContentType "application/json" -Body $body
You should get back:


{
  "result": {
    "msg": "hello"
  }
}

2) Invalid Script (Number Instead of String)

$body = @{
    script = 12345
} | ConvertTo-Json -Compress

Invoke-RestMethod -Method POST -Uri http://localhost:8080/execute -ContentType "application/json" -Body $body
Expected output:


{
  "error": "'script' must be a string and included in the request"
}


3) Missing 'script' Field

$body = @{
    not_script = "print('oops')"
} | ConvertTo-Json -Compress

Invoke-RestMethod -Method POST -Uri http://localhost:8080/execute -ContentType "application/json" -Body $body
Expected output:


{
  "error": "Missing 'script' in request"
}

4)Script Too Big
Try sending a script >10KB. You’ll get:


{
  "error": "Script too large. Max size allowed is 10KB."
}




Important Notes on nsjail
Initially, I tried to sandbox Python code execution using nsjail for enhanced security.

nsjail works perfectly when running locally ( in your Docker container on machine).

However, on Google Cloud Run, nsjail runs into low-level Linux kernel restrictions causing failures (errors with prctl and clone flags).

Because Cloud Run is a managed environment with limited kernel capabilities, nsjail’s sandboxing cannot function properly there.

To work around this, I temporarily switched to running user scripts safely using subprocess with time and memory limits.


# With nsjail locally
![test1](https://github.com/user-attachments/assets/4900d42c-2bf3-476c-a4b6-866c9c5b6ea4)


![test2](https://github.com/user-attachments/assets/62d9c99c-e447-4673-bfac-3cb135ff0692)


![test3](https://github.com/user-attachments/assets/6cf195b6-7df6-4750-960e-67c34bd83375)


# On Google cloud run
![test4](https://github.com/user-attachments/assets/f2a1943a-aa91-4a12-9a0c-d35bb84154dc)


