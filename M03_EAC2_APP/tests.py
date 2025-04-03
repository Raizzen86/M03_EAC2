from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User  # Per verificar la base de dades
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options  # Fem servir Firefox en lloc de Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ['testdb.json']  # Base de dades de prova

    @classmethod
    def setUpClass(cls):
        """Configuració inicial: Obrir Selenium amb Firefox."""
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")  # Executar en mode headless (sense interfície gràfica)
        cls.selenium = webdriver.Firefox(options=opts)
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        """Tancar Selenium després de les proves."""
        cls.selenium.quit()
        super().tearDownClass()

    def test_login_and_add_user(self):
        """Test per comprovar que el superusuari pot accedir i afegir usuaris."""
        self.selenium.get(f"{self.live_server_url}/admin/login/")

        # Iniciar sessió amb el superusuari
        self.selenium.find_element(By.NAME, "username").send_keys("isard")
        self.selenium.find_element(By.NAME, "password").send_keys("pirineus")
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Comprovar que hem iniciat sessió correctament
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")

        # Accedir a la secció d'usuaris
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/")

        # Fer clic a "Add user"
        add_user_link = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="content-main"]//a[contains(@href, "/admin/auth/user/add/")]'))
        )
        add_user_link.click()

        # Verificar que estem a la pàgina d’afegir usuari
        self.assertIn("/admin/auth/user/add/", self.selenium.current_url)

        # Omplir el formulari
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys("Noel")
        self.selenium.find_element(By.NAME, "password1").send_keys("Staff123.")
        self.selenium.find_element(By.NAME, "password2").send_keys("Staff123.")

        # Guardar el nou usuari
        self.selenium.find_element(By.XPATH, '//input[@value="Save"]').click()

        # Marcar el camp "is_staff"
        staff_checkbox = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, "is_staff"))
        )
        if not staff_checkbox.is_selected():
            staff_checkbox.click()

        # Guardar els canvis
        self.selenium.find_element(By.XPATH, '//input[@value="Save"]').click()

        # Verificar que l’usuari s’ha creat correctament a la base de dades
        user = User.objects.filter(username="Noel").first()
        self.assertIsNotNone(user)  # Comprovar que l'usuari existeix
        self.assertTrue(user.is_staff)  # Comprovar que l'usuari té permisos de staff
