set FORKED_BY_MULTIPROCESSING=1
celery -A scheduler worker --concurrency=1 --loglevel=info --logfile=logs/celery_scheduler.log