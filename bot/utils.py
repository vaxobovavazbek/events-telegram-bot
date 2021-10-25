from models.user import User


def get_display_name(user: User) -> str:
    display_name = ''
    if user.first_name:
        display_name = user.first_name
    elif user.username:
        display_name = user.username
    return display_name
