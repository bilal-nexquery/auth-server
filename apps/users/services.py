from apps.users.models import User


def user_create(*, email: str, username: str, password: str, **kwargs) -> User:
    user = User(email=email, username=username)
    user.set_password(password)
    user.save()
    return user
