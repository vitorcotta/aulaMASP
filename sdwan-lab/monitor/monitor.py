import http.server
import json
import os
from pathlib import Path

LOG_FILE = Path("/logs/sdwan_branch.log")


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/status"):
            data = self.read_status()
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Página simples HTML
        body = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <title>SD-WAN Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      body {{
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #020617;
        color: #e5e7eb;
        margin: 0;
        padding: 1.5rem;
      }}
      h1 {{
        margin-top: 0;
      }}
      pre {{
        background: #0f172a;
        padding: 1rem;
        border-radius: 0.75rem;
        max-height: 70vh;
        overflow: auto;
        font-size: 0.8rem;
      }}
    </style>
  </head>
  <body>
    <h1>SD-WAN Monitor</h1>
    <p>Mostrando as últimas linhas de <code>sdwan_branch.log</code>.</p>
    <pre>{self.read_status().get("tail", "")}</pre>
  </body>
</html>
""".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return

    @staticmethod
    def read_status():
        if not LOG_FILE.exists():
            return {"active_path": None, "tail": ""}
        text = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
        lines = text.strip().splitlines()
        tail = "\n".join(lines[-80:])
        active = None
        for line in reversed(lines):
            if "ACTIVE_PATH" in line:
                parts = line.split()
                if len(parts) >= 3:
                    active = parts[2]
                break
        return {"active_path": active, "tail": tail}


def main():
    port = int(os.getenv("MONITOR_PORT", "9090"))
    server = http.server.HTTPServer(("0.0.0.0", port), Handler)
    print(f"[monitor] Escutando em 0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

