# Python Code Execution API

Welcome!
This is a mighty Flask API that safely runs Python code sent via HTTP. It’s built for experimentation and sandboxing, perfect for learning, testing, or running student-submitted code in a safe container.

We use **nsjail** for isolation (read: no rogue infinite loops or imports stealing the show 🚫💻), and Docker to make everything portable and deployment-ready.

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


This project was made to learn, share, and make isolated code execution easier to understand.

