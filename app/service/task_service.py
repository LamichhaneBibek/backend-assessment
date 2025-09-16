import logging
from datetime import datetime
from typing import Dict, Any
from celery import current_task
from celery.exceptions import Retry

from app.core.celery_app import celery_app
from app.core.db_context import session_maker
from app.models.db import TaskLog

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_task_start(task_name: str, task_id: str) -> None:
    """
    Log task start in database
    """
    db = session_maker

    try:
        task_log = TaskLog(
            task_id=task_id,
            task_name=task_name,
            status="pending"
        )
        db.add(task_log)
        db.commit()
        logger.info(f"Task {task_name} ({task_id}) started")
    except Exception as e:
        logger.error(f"Failed to log task start: {e}")
    finally:
        db.close()


def log_task_completion(
    task_id: str,
    status: str,
    result: str = None,
    error_message: str = None
) -> None:
    """
    Log task completion in database
    """
    db = session_maker
    try:
        task_log = db.query(TaskLog).filter(TaskLog.task_id == task_id).first()
        if task_log:
            task_log.status = status
            task_log.result = result
            task_log.error_message = error_message
            task_log.completed_at = datetime.utcnow()
            db.commit()
            logger.info(f"Task {task_id} completed with status: {status}")
    except Exception as e:
        logger.error(f"Failed to log task completion: {e}")
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_email: str, user_name: str) -> Dict[str, Any]:
    """
    Send welcome email to new user (mock implementation)
    This is a background task that simulates sending an email
    """
    task_id = self.request.id
    task_name = "send_welcome_email"

    # Log task start
    log_task_start(task_name, task_id)

    try:
        # Simulate email sending process
        logger.info(f"Sending welcome email to {user_email} for user {user_name}")

        # Mock email content
        email_content = {
            "to": user_email,
            "subject": "Welcome to Arcodify!",
            "body": f"""
            Dear {user_name},

            Welcome to Arcodify! Your account has been successfully created.

            We're excited to have you on board!

            Best regards,
            The Arcodify Team
            """,
            "sent_at": datetime.utcnow().isoformat()
        }

        # Simulate potential failures for testing retry mechanism
        # Uncomment the following lines to test retry functionality
        # import random
        # if random.random() < 0.3:  # 30% chance of failure
        #     raise Exception("Simulated email service failure")

        # Mock successful email sending
        result = {
            "status": "sent",
            "email": user_email,
            "message_id": f"msg_{task_id}",
            "timestamp": datetime.utcnow().isoformat()
        }

        # Log successful completion
        log_task_completion(task_id, "success", str(result))

        logger.info(f"Welcome email sent successfully to {user_email}")
        return result

    except Exception as exc:
        error_message = str(exc)
        logger.error(f"Failed to send welcome email to {user_email}: {error_message}")

        # Retry logic
        if self.request.retries < self.max_retries:
            log_task_completion(task_id, "retry", None, error_message)
            logger.info(f"Retrying task {task_id} in {self.default_retry_delay} seconds")
            raise self.retry(countdown=60, exc=exc)
        else:
            # Max retries reached
            log_task_completion(task_id, "failure", None, error_message)
            return {
                "status": "failed",
                "error": error_message,
                "retries": self.request.retries
            }


@celery_app.task(bind=True)
def cleanup_old_task_logs(self, days_old: int = 30) -> Dict[str, Any]:
    """
    Cleanup old task logs (utility task)
    """
    task_id = self.request.id
    task_name = "cleanup_old_task_logs"

    log_task_start(task_name, task_id)

    try:
        from datetime import timedelta

        db = session_maker
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        # Delete old task logs
        deleted_count = db.query(TaskLog).filter(
            TaskLog.created_at < cutoff_date
        ).delete()

        db.commit()
        db.close()

        result = {
            "deleted_logs": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }

        log_task_completion(task_id, "success", str(result))
        return result

    except Exception as exc:
        error_message = str(exc)
        log_task_completion(task_id, "failure", None, error_message)
        return {
            "status": "failed",
            "error": error_message
        }


@celery_app.task(bind=True)
def health_check_task(self) -> Dict[str, Any]:
    """
    Simple health check task for monitoring
    """
    task_id = self.request.id
    task_name = "health_check"

    log_task_start(task_name, task_id)

    result = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "worker_id": task_id
    }

    log_task_completion(task_id, "success", str(result))
    return result


# Task discovery for Celery
__all__ = [
    "send_welcome_email",
    "cleanup_old_task_logs",
    "health_check_task"
]
