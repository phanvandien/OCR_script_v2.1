import os
import multiprocessing 

bind = "unix:/home/dienpv/OCR_script/gunicorn.sock"
backlog = 2048

workers = multiprocessing.cpu_count() * 2 + 1
threads = 4
worker_class = "sync"
worker_connections = 1000
timeout = 1800
keepalive = 2
max_requests = 0
max_requests_jitter = 0

worker_tmp_dir = "/dev/shm"
preload_app = True

errorlog = "/home/dienpv/OCR_script/logs/gunicorn_error.log"
accesslog = "/home/dienpv/OCR_script/logs/gunicorn_access.log"
loglevel = "debug"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

proc_name = "ocr_script_gunicorn"

limit_request_line = 8190
limit_request_fields = 200
limit_request_field_size = 16384

worker_rlimit_nofile = 4096
worker_rlimit_core = 0

wsgi_app = 'ocr.wsgi:application'

def when_ready(server):
   server.log.info("Server is ready. Spawning workers")

def worker_int(server):
   server.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
   server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
   server.log.info("Worker spawned (pid: %s)",worker.pid)

def post_worker_init(worker):
   worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
   worker.log.info("Worker aborted (pid: %s)", worker.pid)

