from http.server import BaseHTTPRequestHandler, HTTPServer
import time


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        body = f"OK - app datacenter - {now}\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, fmt, *args):
        return


def main():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("[app] HTTP server escutando em 0.0.0.0:8080")
    server.serve_forever()


if __name__ == "__main__":
    main()

