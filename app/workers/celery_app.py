import logging
from app.config import settings

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    celery_app = Celery(
        "rag",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND
    )
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
except ImportError:
    logger.warning("Celery module not installed in Python environment. Using MockCelery fallback wrapper.")
    class DummyTaskResult:
        def __init__(self, res):
            self._res = res
        def get(self, timeout=None):
            return self._res

    class MockTaskSelf:
        def retry(self, exc=None, countdown=2):
            logger.debug(f"MockTaskSelf retrying: {exc}")
            raise exc if exc else RuntimeError("MockTaskSelf retry")

    class MockCelery:
        def task(self, *args, **kwargs):
            def decorator(func):
                def delay(*task_args, **task_kwargs):
                    is_bound = kwargs.get('bind', False)
                    if is_bound:
                        res = func(MockTaskSelf(), *task_args, **task_kwargs)
                    else:
                        res = func(*task_args, **task_kwargs)
                    return DummyTaskResult(res)
                func.delay = delay
                return func
            if len(args) == 1 and callable(args[0]):
                return decorator(args[0])
            return decorator

    celery_app = MockCelery()