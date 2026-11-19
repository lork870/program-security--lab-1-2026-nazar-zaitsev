import json
import logging
import os
import uuid
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "liberink_app.log")

SENSITIVE_KEYS = {"password", "token", "access_token", "secret", "authorization"}


def mask_sensitive(data: dict) -> dict:
    masked = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_KEYS:
            masked[k] = "***REDACTED***"
        else:
            masked[k] = v
    return masked


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "component": getattr(record, "component", "api"),
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", "anonymous"),
            "ip": getattr(record, "ip", "127.0.0.1"),
            "action": getattr(record, "action", "event"),
            "result": getattr(record, "result", "ok"),
            "details": mask_sensitive(getattr(record, "details", {})),
        }
        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("liberink")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=4096, backupCount=3, encoding="utf-8")
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)


class SecurityMonitor:
    def __init__(self, fail_threshold=3):
        self.fail_threshold = fail_threshold
        self.failed_logins = {}
        self.total_requests = 0
        self.error_count = 0

    def record_event(self, level, component, user_id, ip, action, result, details=None):
        req_id = f"req-{uuid.uuid4().hex[:8]}"
        self.total_requests += 1
        if level >= logging.ERROR:
            self.error_count += 1

        logger.log(
            level,
            action,
            extra={
                "component": component,
                "request_id": req_id,
                "user_id": user_id,
                "ip": ip,
                "action": action,
                "result": result,
                "details": details or {},
            },
        )

        if action == "auth.login" and result == "failed":
            self.failed_logins[ip] = self.failed_logins.get(ip, 0) + 1
            if self.failed_logins[ip] >= self.fail_threshold:
                logger.log(
                    logging.CRITICAL,
                    "monitoring.alert",
                    extra={
                        "component": "monitor",
                        "request_id": req_id,
                        "user_id": user_id,
                        "ip": ip,
                        "action": "alert.bruteforce_detected",
                        "result": "triggered",
                        "details": {"failed_attempts": self.failed_logins[ip]},
                    },
                )
                print(f"[ALERT] Brute-force detected from IP {ip} ({self.failed_logins[ip]} failed attempts)!")


if __name__ == "__main__":
    monitor = SecurityMonitor(fail_threshold=3)

    monitor.record_event(logging.INFO, "system", "system", "127.0.0.1", "app.startup", "ok", {"env": "production"})
    monitor.record_event(
        logging.INFO, "auth", "uid_101", "203.0.113.10", "auth.login", "success",
        {"password": "MySecretPassword123", "access_token": "eyJhbGciOiJSUzI1NiJ9.secret"}
    )
    monitor.record_event(logging.INFO, "books", "uid_101", "203.0.113.10", "book_element.update", "success", {"element_id": 42})

    # Симуляція brute-force атаки
    for attempt in range(1, 4):
        monitor.record_event(
            logging.WARNING, "auth", "uid_admin", "185.220.101.22", "auth.login", "failed",
            {"attempt": attempt, "password": f"guess_{attempt}"}
        )

    print(f"\n--- Monitoring Summary ---")
    print(f"Total events: {monitor.total_requests} | Errors: {monitor.error_count} | Log file: {LOG_FILE}")
    print("\n--- Generated JSON Logs ---")
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        print(f.read())