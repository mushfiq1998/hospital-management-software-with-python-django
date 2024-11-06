def notification_count(request):
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        print(f"Debug: Unread notifications for {request.user.username}: {unread_count}")
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0} 