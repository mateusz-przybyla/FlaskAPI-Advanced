import os
import redis
from rq import Worker, Queue

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
email_queue = Queue("emails", connection=redis_client)

if __name__ == "__main__":
    worker = Worker([email_queue])
    worker.work()