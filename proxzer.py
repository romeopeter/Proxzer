from flask import Flask, request, Response
from flask_cors import CORS
import requests
from urllib.parse import urlparse

server = Flask(__name__)

CORS(server)

# API and proxy endpoint
ENDPOINT_URL = "https://mailjet.com/api/vi/..."
PROXY_ENDPOINT = "/corsproxy/"
ALLOWED_METHODS = {"GET": "GET", "HEAD": "HEAD", "POST": "POST", "OPTIONS": "OPTIONS"}


# CORS preflight request
@server.route(PROXY_ENDPOINT, methods=["OPTIONS"])
def handle_preflight():
    CORS_options = (
        request.headers.get("Origin")
        and request.headers.get("Access-Control-Request-Method")
        and request.headers.get("Access-Control-Request-Headers")
    )

    if CORS_options:
        response_headers = {
            "Access-Control-Allow-Origin": request.headers.get("Origin"),
            "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS",
            "Access-Control-Allow-Headers": request.headers.get(
                "Access-Control-Request-Headers"
            ),
        }
        return Response(headers=response_headers)
    else:
        Response(headers={"Allow": "GET, HEAD, POST, OPTIONS"})


@server.route(PROXY_ENDPOINT, methods=list(ALLOWED_METHODS.values()))
def handle_endpoint():
    # Grab intended endpoint from request
    endpoint = request.args.get("endpointUrl", ENDPOINT_URL)

    # Rewrite request origin to use intended endpoint as origin to stop cross-site check
    request.headers["Origin"] = urlparse(endpoint).netloc  # Warning: 'urlparse' may fail. use any alternative

    # Make request to server
    response = requests.request(
        request.method, ENDPOINT_URL, headers=request.headers, data=request.data
    )

    # Modify headers
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin")
    response.headers["Vary"] = request.headers.get("Origin")

    return Response(response.content, status=response.status_code)


if __name__ is "__main__":
    server.run()
