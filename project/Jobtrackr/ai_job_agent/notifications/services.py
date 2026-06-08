import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Notification
from jobs.models import Job

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_alert(user, title, message, notification_type='system'):
        """
        Creates a notification database record and sends an email alert if user preferences allow.
        """
        # 1. Create DB Notification
        notif = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )
        
        # 2. Check settings for email dispatch
        pref, _ = notif.user.notification_settings.user.notification_settings, True # safe access
        pref = getattr(user, 'notification_settings', None)
        
        if pref and pref.email_alerts:
            try:
                subject = f"[AI Job Agent] {title}"
                email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', 'agent@jobtrackr.ai')
                recipient_list = [user.email]
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=email_from,
                    recipient_list=recipient_list,
                    fail_silently=True
                )
                logger.info(f"Notification email dispatched to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send email alert: {str(e)}")
                
        return notif

    @staticmethod
    def send_daily_digest(user):
        """
        Compiles jobs fetched in the last 24 hours and emails a summary digest.
        """
        pref = getattr(user, 'notification_settings', None)
        if not pref or not pref.daily_digest:
            logger.info(f"Daily digest is disabled for user {user.username}")
            return False

        # Fetch jobs discovered in last 24 hours
        yesterday = timezone.now() - timedelta(days=1)
        recent_jobs = Job.objects.filter(fetched_at__gte=yesterday, is_active=True)

        if not recent_jobs.exists():
            logger.info("No recent jobs discovered in last 24h for daily digest.")
            return False

        # Format message content
        subject = "[AI Job Agent] Daily Jobs Digest Summary"
        email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', 'agent@jobtrackr.ai')
        recipient_list = [user.email]
        
        body = f"Hello {user.username},\n\nHere is your daily digest of jobs discovered in the last 24 hours:\n\n"
        
        for job in recent_jobs[:10]: # Limit to top 10
            body += f"- {job.title} at {job.company} ({job.location|default:'Remote'})\n"
            body += f"  Source: {job.get_source_display()} | Link: {job.url}\n\n"
            
        body += "Login to your dashboard to check matching ratings and generate tailored cover letters.\n\nBest,\nAI Job Agent Team"
        
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=email_from,
                recipient_list=recipient_list,
                fail_silently=True
            )
            
            # Log inside DB too
            Notification.objects.create(
                user=user,
                title="Daily Jobs Digest Sent",
                message=f"Compiled and emailed {recent_jobs.count()} recently discovered jobs to your inbox.",
                notification_type='digest'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send daily digest email: {str(e)}")
            return False
