from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User  # Importar el modelo de usuario de Django
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MySeleniumTests(StaticLiveServerTestCase):
    # Cargar una base de datos de prueba
    fixtures = ['testdb.json']

    @classmethod
    def setUpClass(cls):
        """Configuración inicial: Abrir Selenium."""
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")  # Ejecutar en modo headless
        cls.selenium = webdriver.Chrome(options=opts)
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        """Cerrar Selenium después de las pruebas."""
        cls.selenium.quit()
        super().tearDownClass()

    def test_login_and_add_user(self):
        """Test para comprobar que el superusuario puede acceder y agregar usuarios."""
        # 1. Navegar a la página de inicio de sesión
        self.selenium.get(f"{self.live_server_url}/admin/login/")

        # 2. Iniciar sesión con el superusuario
        print("🔍 Verificando la página de login...")
        self.selenium.find_element(By.NAME, "username").send_keys("isard")
        self.selenium.find_element(By.NAME, "password").send_keys("pirineus")
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # 3. Comprobar que hemos iniciado sesión correctamente
        print("✅ Comprobando título de la página post-login...")
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")
        print("✅ Test de login correcto!")

        # 4. Acceder a la sección de usuarios
        print("🔍 Navegando a la sección de usuarios...")
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/")

        # 5. Acceder al enlace "Add user" con un XPath más específico
        print("🔍 Buscando el enlace de 'Add user'...")
        add_user_link = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="content-main"]//a[contains(@href, "/admin/auth/user/add/")]'))
        )
        add_user_link.click()

        # 6. Verificar la URL actual para asegurarse de que estamos en la página de agregar usuario
        print("🔍 Comprobando la URL actual...")
        self.assertIn("/admin/auth/user/add/", self.selenium.current_url)

        # 7. Rellenar el formulario para agregar un usuario
        print("✅ Rellenando el formulario de nuevo usuario...")
        username_field = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys("Noel")
        self.selenium.find_element(By.NAME, "password1").send_keys("Staff123.")
        self.selenium.find_element(By.NAME, "password2").send_keys("Staff123.")

        # 8. Guardar el usuario
        print("✅ Guardando el nuevo usuario...")
        self.selenium.find_element(By.XPATH, '//input[@value="Save"]').click()

        # 9. Marcar el campo "is_staff"
        print("🔍 Verificando la selección del campo 'is_staff'...")
        staff_checkbox = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "is_staff"))
        )
        if not staff_checkbox.is_selected():
            staff_checkbox.click()

        # 10. Guardar los cambios del usuario
        print("✅ Guardando los cambios del usuario...")
        self.selenium.find_element(By.XPATH, '//input[@value="Save"]').click()

        # 11. Verificar que el usuario se ha creado correctamente en la base de datos de pruebas
        print("🔍 Verificando que el usuario existe en la base de datos de prueba...")
        self.assertTrue(User.objects.filter(username="Noel").exists())
        print("✅ Usuario creado correctamente en la base de datos de prueba!")
