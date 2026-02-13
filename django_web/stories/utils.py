def get_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key
