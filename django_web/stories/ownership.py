from django.shortcuts import get_object_or_404
from .models import StoryOwnership

def require_owner_or_admin(request, story_id: int):
    if request.user.is_staff:
        return 
    get_object_or_404(StoryOwnership, story_id=story_id, owner=request.user)
