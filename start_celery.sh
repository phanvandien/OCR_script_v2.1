#!/bin/bash

cd /home/dienpv/OCR_script
source venv/bin/activate

export DJANGO_SETTINGS_MODULE=ocr.settings
export PYTHONPATH=/home/dienpv/OCR_script

pkill -f "celery worker"

sleep 2

./venv/bin/celery -A ocr worker --loglevel=info --concurrency=2 --logfile=/home/dienpv/OCR_script/logs/celery.log

