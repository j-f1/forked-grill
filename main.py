import sys
import threading

sys.path.append("backend")

import chat_worker
import web_worker

if __name__ == "__main__":
    threading.Thread(target=chat_worker.start).start()
    web_worker.start()
