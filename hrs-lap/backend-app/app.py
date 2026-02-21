from flask import Flask, request, make_response
import time
import uuid

app = Flask(__name__)

# 🔴 In-memory session store (INTENTIONALLY VULNERABLE)
SESSIONS = {}

@app.before_request
def log_request():
    req_id = str(uuid.uuid4())

    print("\n===== BACKEND REQUEST START =====", flush=True)
    print(f"Request-ID: {req_id}", flush=True)
    print(f"Timestamp: {time.time()}", flush=True)
    print(f"Method: {request.method}", flush=True)
    print(f"Path: {request.path}", flush=True)
    print(f"Headers:", flush=True)

    for k, v in request.headers.items():
        print(f"  {k}: {v}", flush=True)

    body = request.get_data()
    print(f"Body-Length: {len(body)}", flush=True)
    print(f"Body-Raw: {body}", flush=True)
    print("===== BACKEND REQUEST END =====\n", flush=True)


@app.route("/health")
def health():
    return "OK", 200


@app.route("/login", methods=["POST"])
def login():
    # Parse username from form body
    username = request.form.get("username")

    if not username:
        return "Missing username\n", 400

    # Create session
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = username

    resp = make_response(f"Login successful as {username}\n")
    resp.set_cookie("session_id", session_id)

    return resp


@app.route("/profile")
def profile():
    session_id = request.cookies.get("session_id")

    if not session_id or session_id not in SESSIONS:
        return "Unauthorized – no valid session\n", 401

    username = SESSIONS[session_id]
    return f"Profile page of user: {username}\n"


@app.route("/log")
def log_access():
    return "Log entry created\n", 200
