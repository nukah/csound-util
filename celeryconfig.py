BROKER_HOST = "mighty"
BROKER_PORT = 5672
BROKER_USER = "nuke"
BROKER_PASSWORD = "1"
BROKER_VHOST = "mighty"
CELERY_RESULT_BACKEND = "amqp"
CELERY_IMPORTS = ("asound.dispatch.worker", )