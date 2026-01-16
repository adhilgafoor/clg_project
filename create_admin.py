from django.contrib.auth.models import User, Group

# Create 'admin' group
group, created = Group.objects.get_or_create(name='admin')

# Create superuser 'admin'
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    user.groups.add(group)
    user.save()
    print("Admin user created and added to 'admin' group.")
else:
    user = User.objects.get(username='admin')
    user.groups.add(group)
    print("Admin user already exists. Added to 'admin' group.")
