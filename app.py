from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Netlify LUMNYX app URL
TARGET = "https://lumnyx.netlify.app"

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def proxy(path):
    # Construct full target URL
    target_url = f"{TARGET}/{path}"
    if request.query_string:
        target_url += "?" + request.query_string.decode()

    # Forward the request to Netlify
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers={k: v for k, v in request.headers if k.lower() != "host"},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    # Strip headers that can block embedding
    excluded_headers = [
        "content-encoding", "transfer-encoding", "connection",
        "x-frame-options", "content-security-policy",
        "strict-transport-security"
    ]
    headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded_headers]

    # Optional: allow CORS for text/image requests
    headers.append(("Access-Control-Allow-Origin", "*"))

    return Response(resp.content, resp.status_code, headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
