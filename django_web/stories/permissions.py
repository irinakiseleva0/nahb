from django.contrib.auth.decorators import user_passes_test

def is_author(user):
    return (
        user.is_authenticated
        and (user.is_staff or user.groups.filter(name="Author").exists())
    )

author_required = user_passes_test(is_author, login_url="/accounts/login/")
