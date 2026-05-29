# your_app/management/commands/ping_service.py

from django.core.management.base import BaseCommand
import time
import requests

URL_TO_HIT = "http://portal.mnh.or.tz/visitt/29"  # Replace with actual URL

class Command(BaseCommand):
    help = "Ping a URL every 2 minutes"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting ping loop..."))
        while True:
            try:
                response = requests.get(URL_TO_HIT)
                self.stdout.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Status: {response.status_code}")
            except Exception as e:
                self.stderr.write(f"Error: {e}")
            time.sleep(10)
