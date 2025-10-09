from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone

from myapp.models import Usuario  # existe aún

class Command(BaseCommand):
    help = "Copia myapp.Usuario a auth.User, preservando hash y asignando grupo 'usuario'."

    def handle(self, *args, **kwargs):
        grp, _ = Group.objects.get_or_create(name='usuario')  # trabajador

        created, updated, skipped = 0, 0, 0
        for u in Usuario.objects.all():
            username = (u.username or "").strip()
            email = (u.correo or "").strip().lower()

            try:
                user = User.objects.get(username__iexact=username)
                # Actualiza email si está vacío o distinto
                if email and user.email != email:
                    user.email = email
                    user.save(update_fields=["email"])
                    updated += 1
                # Asegura pertenencia a 'usuario' si no es superuser
                if not user.is_superuser and not user.groups.filter(name='usuario').exists():
                    user.groups.add(grp)
                skipped += 1
                continue
            except User.DoesNotExist:
                pass

            user = User(
                username=username,
                email=email,
                is_active=True,
                date_joined=u.created_at or timezone.now(),
            )
            # Copiamos el HASH tal cual (fue creado con make_password de Django)
            user.password = u.password
            user.save()
            user.groups.add(grp)
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"auth.User creados={created}, emails_actualizados={updated}, ya_existen={skipped}"
        ))
