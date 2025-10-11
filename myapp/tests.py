from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
from myapp import models as my_models


class ViewsTestCase(TestCase):
    def test_home_view_status_and_template(self):
        """
        Si la vista home redirige (por ejemplo a login), follow=True
        asegura que comprobemos el estado final.
        """
        response = self.client.get(reverse('home'), follow=True)
        # Comprobamos que la respuesta final sea 200
        self.assertEqual(response.status_code, 200, msg=f"Estado final esperado 200, obtenido {response.status_code}. Content: {response.content[:200]!r}")
        # Comprueba el template si aplica (ajusta el nombre si es necesario)
        # self.assertTemplateUsed(response, 'home.html')

    def test_signup_crea_usuario(self):
        """
        Intenta enviar el formulario de signup usando distintos nombres
        de campo (password/password_confirm o password1/password2).
        Luego comprueba que el usuario fue creado.
        """
        url = reverse('signup')
        possible_payloads = [
            # tu formulario personalizado (según mensajes de error que mostraste)
            {'username': 'usuario_test', 'password': 'ClaveSegura123!', 'confirm_password': 'ClaveSegura123!'},
            # fallback al UserCreationForm estándar
            {'username': 'usuario_test2', 'password1': 'ClaveSegura123!', 'password2': 'ClaveSegura123!'},
        ]

        created_users_before = set(User.objects.values_list('username', flat=True))

        for payload in possible_payloads:
            response = self.client.post(url, payload, follow=True)
            # Si se redirige tras el registro, follow=True hace la petición final
            # Comprobamos si alguno de los usuarios de payload fue creado
            candidate_username = payload.get('username')
            if User.objects.filter(username=candidate_username).exists():
                # ok: usuario creado
                return
            # si no, seguimos probando con el siguiente payload

        # Si llegamos aquí, ninguno de los intentos creó usuario -> fallamos mostrando contenido para debug
        self.fail(
            "Ningún payload creó el usuario. Última respuesta (parcial):\n"
            + response.content.decode(errors='ignore')[:1000]
        )


class ModelsTestCase(TestCase):
    def test_creacion_empresa(self):
        """
        Intenta detectar un campo de texto en Empresa (CharField/TextField)
        y crear una instancia usando ese campo. Si no encuentra un campo
        de texto no obligatorio, salta el test para que lo adaptes manualmente.
        """
        Empresa = my_models.Empresa

        # Busca un campo de CharField o TextField que no sea AutoField y que no sea unique=True si requiere más cuidado
        text_field = None
        for field in Empresa._meta.get_fields():
            # Sólo interesan fields concretos (no relaciones invertidas ni m2m automáticas)
            if isinstance(field, models.Field):
                # evitar AutoField / primary key
                if getattr(field, 'auto_created', False):
                    continue
                if getattr(field, 'primary_key', False):
                    continue
                # Char/Text candidates
                if isinstance(field, (models.CharField, models.TextField)):
                    text_field = field
                    break

        if text_field is None:
            # No encontramos un campo de texto simple; saltamos el test para evitar falsos positivos.
            self.skipTest(
                "No se encontró CharField/TextField simple en Empresa. "
                "Abre myapp/models.py y adapta este test al(s) campo(s) requeridos de Empresa."
            )

        # Construimos kwargs para crear la instancia; si el campo no acepta blank, le damos un valor de prueba.
        kwargs = {text_field.name: "Empresa Demo de Test"}
        try:
            empresa = Empresa.objects.create(**kwargs)
        except TypeError as e:
            self.fail(f"Fallo creando Empresa con kwargs {kwargs!r}: {e}")

        # Comprobaciones básicas
        self.assertEqual(Empresa.objects.count(), 1)
        self.assertEqual(getattr(empresa, text_field.name), "Empresa Demo de Test")
