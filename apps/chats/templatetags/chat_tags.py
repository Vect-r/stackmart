from django import template

register = template.Library()

@register.filter
def unread_count_for(conversation, user):
    """
    Returns the count of unread messages in the conversation 
    that were NOT sent by the provided user.
    """
    if not user:
        return 0
    return conversation.messages.filter(is_read=False).exclude(sender=user).count()