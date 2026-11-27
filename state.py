import threading
import queue

is_ds3 = threading.Event()
stop = threading.Event()
frames = queue.Queue(maxsize=1)

channel_login = ""
stream_title = ""
