from flask import Flask, request, Response, stream_with_context
import requests

app = Flask(__name__)

# Netlify LUMNYX app
TARGET = "https://lumnyx.netlify.app"

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "OPTIONS"])
def proxy(path):
    # Construct full URL
    target_url = f"{TARGET}/{path}"
    if request.query_string:
        target_url += "?" + request.query_string.decode()

    # Forward the request
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers={k: v for k, v in request.headers if k.lower() != "host"},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=True,
        stream=True
    )

    # Copy headers except ones that block embedding
    excluded_headers = ["x-frame-options", "content-security-policy", "strict-transport-security"]
    headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded_headers]

    # Ensure correct CORS so browser can load assets
    headers.append(("Access-Control-Allow-Origin", "*"))

    # Stream content to avoid breaking large JS/CSS files
    return Response(stream_with_context(resp.raw), status=resp.status_code, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
