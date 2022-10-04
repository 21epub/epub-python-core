import logging
from celery.app.task import Task

logger = logging.getLogger("django")


class CeleryTaskThrowExceptionLogging(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            f"Task {task_id} get exception: \nkwargs: {kwargs} \nwith Traceback: {einfo}"
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
