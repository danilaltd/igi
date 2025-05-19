from django.contrib.auth.hashers import make_password

password = 'admin'
hashed_password = make_password(password)
print(f"Password hash for 'admin': {hashed_password}") 