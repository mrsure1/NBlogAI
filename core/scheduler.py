import json
import threading
import time
from datetime import datetime
from pathlib import Path

QUEUE_PATH = Path(__file__).parent.parent / "data" / "post_queue.json"


def load_queue() -> list:
    if not QUEUE_PATH.exists():
        return []
    try:
        return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_queue(queue: list):
    QUEUE_PATH.parent.mkdir(exist_ok=True)
    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")


def add_to_queue(post_data: dict, scheduled_time: str):
    queue = load_queue()
    queue.append({
        "id": int(time.time()),
        "scheduled_time": scheduled_time,
        "status": "pending",
        "post_data": post_data,
    })
    save_queue(queue)


def remove_from_queue(item_id: int):
    queue = load_queue()
    queue = [q for q in queue if q.get("id") != item_id]
    save_queue(queue)


def get_pending_posts() -> list:
    now = datetime.now()
    results = []
    queue = load_queue()
    for item in queue:
        if item.get("status") != "pending":
            continue
        try:
            scheduled = datetime.strptime(item["scheduled_time"], "%Y-%m-%d %H:%M")
            if scheduled <= now:
                results.append(item)
        except ValueError:
            pass
    return results


class SchedulerThread(threading.Thread):
    def __init__(self, publish_callback):
        super().__init__(daemon=True)
        self.publish_callback = publish_callback
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            pending = get_pending_posts()
            for item in pending:
                try:
                    self.publish_callback(item["post_data"])
                    queue = load_queue()
                    for q in queue:
                        if q.get("id") == item.get("id"):
                            q["status"] = "published"
                    save_queue(queue)
                except Exception as e:
                    print(f"예약 발행 오류: {e}")
            self._stop_event.wait(60)

    def stop(self):
        self._stop_event.set()
