

def user_directory_path(instance, filename):
    username = instance.user.username
    return f'user_{username}/{filename}'