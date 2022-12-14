import os 
from celery import Celery

#celery django settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopproject.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
app = Celery('shopproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
