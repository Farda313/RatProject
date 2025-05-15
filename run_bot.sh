#!/bin/bash
# نام فایل: run_bot.sh

MAX_RETRIES=5
RETRY_DELAY=3

for ((i=1; i<=$MAX_RETRIES; i++)); do
    echo "تلاش $i از $MAX_RETRIES..."
    python main.py 2>&1 | tee -a bot.log
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "ربات با موفقیت اجرا شد"
        exit 0
    else
        echo "خطا در اجرا، انتظار برای تلاش مجدد..."
        sleep $RETRY_DELAY
    fi
done

echo "حداکثر تعداد تلاش‌ها انجام شد. بررسی لاگ‌ها ضروری است"
exit 1
