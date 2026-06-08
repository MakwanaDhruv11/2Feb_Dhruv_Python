from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.services import NotificationService

class Command(BaseCommand):
    help = "Dispatches daily email digests compiling recently discovered jobs to subscribed users."

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.filter(is_active=True)
        self.stdout.write(f"Commencing daily digest run for {users.count()} users...")
        
        success_count = 0
        for user in users:
            if not user.email:
                continue
            try:
                sent = NotificationService.send_daily_digest(user)
                if sent:
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Successfully sent digest to {user.username}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed for user {user.username}: {str(e)}"))
                
        self.stdout.write(self.style.SUCCESS(f"Completed! Sent daily digests to {success_count} users."))
