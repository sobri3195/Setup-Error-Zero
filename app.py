import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HOST = "0.0.0.0"
PORT = 5000
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"

WEIGHTS = {
    "translation": 0.7,
    "rotation": 0.3,
}


class SetupErrorZeroHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send_html(TEMPLATE_PATH.read_text(encoding="utf-8"))
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        if self.path != "/api/recommend":
            self._send_json({"error": "Not found"}, status=404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON payload"}, status=400)
            return

        tx = float(payload.get("tx_mm", 0.0))
        ty = float(payload.get("ty_mm", 0.0))
        tz = float(payload.get("tz_mm", 0.0))
        rx = float(payload.get("rx_deg", 0.0))
        ry = float(payload.get("ry_deg", 0.0))
        rz = float(payload.get("rz_deg", 0.0))

        translation_error = abs(tx) + abs(ty) + abs(tz)
        rotation_error = abs(rx) + abs(ry) + abs(rz)

        risk_score = (
            WEIGHTS["translation"] * translation_error
            + WEIGHTS["rotation"] * rotation_error
        )

        recommendation = {
            "shift_mm": {"x": round(-tx, 2), "y": round(-ty, 2), "z": round(-tz, 2)},
            "rotation_deg": {
                "pitch": round(-rx, 2),
                "roll": round(-ry, 2),
                "yaw": round(-rz, 2),
            },
        }

        if risk_score >= 8:
            action = "Koreksi wajib + repeat imaging sebelum beam on"
        elif risk_score >= 4:
            action = "Koreksi setup direkomendasikan, validasi oleh RTT/dokter"
        else:
            action = "Lanjutkan dengan monitoring, tanpa repeat imaging"

        self._send_json(
            {
                "risk_score": round(risk_score, 2),
                "translation_error_mm": round(translation_error, 2),
                "rotation_error_deg": round(rotation_error, 2),
                "action": action,
                "recommendation": recommendation,
                "note": "Output AI wajib ditinjau oleh RTT/terapis radiasi dan/atau dokter.",
            }
        )


def run_server():
    server = HTTPServer((HOST, PORT), SetupErrorZeroHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
