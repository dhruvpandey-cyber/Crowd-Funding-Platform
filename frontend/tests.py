from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from django.core.management import call_command
import time

class FrontendSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Run migrations and seed demo data
        call_command('migrate', verbosity=0)
        call_command('seed_demo_data')
        # Set up Chrome WebDriver
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Commented out to show browser
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        cls.selenium = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_home_page_loads(self):
        self.selenium.get(self.live_server_url)
        self.assertIn("CrowdSpark", self.selenium.title)
        # Check if main elements are present
        self.assertTrue(self.selenium.find_element(By.TAG_NAME, 'h1'))

    def test_auth_page_loads(self):
        self.selenium.get(self.live_server_url + '/auth/')
        self.assertIn("Login & Register", self.selenium.title)
        # Check login form
        login_form = self.selenium.find_element(By.ID, 'login-form')
        self.assertIsNotNone(login_form)
        # Check register form
        register_form = self.selenium.find_element(By.ID, 'register-form')
        self.assertIsNotNone(register_form)

    def test_login_success(self):
        self.selenium.get(self.live_server_url + '/auth/')
        # Fill login form
        username_field = self.selenium.find_element(By.NAME, 'username')
        password_field = self.selenium.find_element(By.NAME, 'password')
        login_button = self.selenium.find_element(By.CSS_SELECTOR, '#login-form button')

        username_field.send_keys('backer_demo')
        password_field.send_keys('Backer@12345')
        login_button.click()

        # Wait for redirect or message
        WebDriverWait(self.selenium, 10).until(
            lambda driver: 'dashboard' in driver.current_url or driver.find_element(By.ID, 'auth-message').is_displayed()
        )
        # Check if redirected to dashboard or message shown
        self.assertTrue('dashboard' in self.selenium.current_url or 'Welcome' in self.selenium.page_source)

    def test_campaigns_page_loads(self):
        self.selenium.get(self.live_server_url + '/campaigns/')
        self.assertIn("Campaigns", self.selenium.title)
        # Wait for campaigns to load
        WebDriverWait(self.selenium, 10).until(
            lambda driver: len(driver.find_elements(By.CLASS_NAME, 'card')) > 0
        )
        # Check if campaigns are listed
        campaigns = self.selenium.find_elements(By.CLASS_NAME, 'card')
        self.assertGreater(len(campaigns), 0)

    def test_create_campaign_page_loads(self):
        self.selenium.get(self.live_server_url + '/create/')
        self.assertIn("Start Campaign", self.selenium.title)
        # Check if form is present
        form = self.selenium.find_element(By.TAG_NAME, 'form')
        self.assertIsNotNone(form)

    def test_campaign_detail_page(self):
        # Assume campaign ID 1 from seed data
        self.selenium.get(self.live_server_url + '/campaigns/1/')
        self.assertIn("Campaign Detail", self.selenium.title)
        # Check elements
        self.assertTrue(self.selenium.find_element(By.ID, 'campaign-detail-card'))

    # Add more tests as needed

    def test_navigation(self):
        self.selenium.get(self.live_server_url)
        # Click on campaigns link
        campaigns_link = self.selenium.find_element(By.LINK_TEXT, 'Campaigns')
        campaigns_link.click()
        WebDriverWait(self.selenium, 10).until(
            lambda driver: 'campaigns' in driver.current_url
        )
        self.assertIn('campaigns', self.selenium.current_url)
