from .models import Notification
from django.utils import timezone

def create_notification(recipient, title, message, notification_type='general', priority='medium', link=None, icon='fa-bell'):
    """
    Create a new notification
    
    Args:
        recipient: User object who will receive the notification
        title: String title of notification
        message: String message content
        notification_type: String type of notification (from NOTIFICATION_TYPES)
        priority: String priority level (from PRIORITY_LEVELS)
        link: Optional URL string to related content
        icon: Font Awesome icon class string
    """
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        link=link,
        icon=icon
    )
    return notification

def create_bulk_notifications(recipients, title, message, **kwargs):
    """
    Create notifications for multiple recipients
    """
    notifications = []
    for recipient in recipients:
        notification = create_notification(recipient, title, message, **kwargs)
        notifications.append(notification)
    return notifications 