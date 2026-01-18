from django.contrib.auth import get_user_model
from django.db.utils import OperationalError

def create_admin():
    try:
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123"
            )
            print("Admin user created")
    except OperationalError:
        pass

create_admin()
