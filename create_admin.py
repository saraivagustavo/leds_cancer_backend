import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leds_cancer_backend.settings")

import sys
sys.path.insert(0, "leds_cancer_backend")

django.setup()

from authentication.models import User

username = "integracao"
email = "integracao@admin.com"
password = "admin123"

if User.objects.filter(username=username).exists():
    print(f"Usuário '{username}' já existe. Atualizando para superuser...")
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
else:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        is_active=True,
    )

print(f"✓ Superusuário criado/atualizado com sucesso!")
print(f"  Username : {username}")
print(f"  Senha    : {password}")
print(f"  Acesse   : http://localhost:8000/admin/")
