from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Chrome options
options = Options()
# If you want to use Brave instead of Chrome:
# options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# Automatically download correct ChromeDriver
service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=options)

driver.get("https://example.com")
print(driver.title)

driver.quit()
