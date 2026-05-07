"""
Context processor to inject unread notification count into all templates.
"""

from .models import Notification


def notifications_processor(request):
    """Add unread notification count to template context."""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notification_count': unread_count}
    return {'unread_notification_count': 0}
