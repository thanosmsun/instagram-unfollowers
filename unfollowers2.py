from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
from openpyxl import Workbook
from webdriver_manager.chrome import ChromeDriverManager

class InstaUnfollowers:
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--log-level=3")  # Suppress DevTools logs
        self.chrome_options.add_argument("--ignore-certificate-errors")  # Suppress SSL errors
        self.driver = None
        self.username = input("Please enter your Instagram username: ")
        print("After you complete the log in press enter in the command promt.")
        print("Don't close any window and make sure your pc doesn't close.")

    def start_browser(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        self.driver.get("https://www.instagram.com")
        username_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
        username_field.send_keys(self.username)
        input("Log in and then press Enter here to continue...")

    def get_unfollowers(self): 
        print("Now let's find your fake firends!!!")
        accountUrl = f"https://instagram.com/{self.username}/"
        self.driver.get(accountUrl)
        self.click_link('followers')
        followers_list = self.get_people("followers")
        self.driver.get(accountUrl)
        self.click_link('following')
        following_list = self.get_people("following")
        not_following_back = [user for user in following_list if user not in followers_list]
        not_following_back.sort()
        print("These people are not following you back:")
        for name in not_following_back:
            print(name)
        print(f"Total: {len(not_following_back)}")
        return not_following_back

    def click_link(self, link_type):
        wait = WebDriverWait(self.driver, 10)
        if link_type == "followers":
            link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers/')]")))
        elif link_type == "following":
            link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following/')]")))
        link.click()
        sleep(2)  # Giving it some time to load

    def get_people(self, list_type):
        wait = WebDriverWait(self.driver, 10)
        sleep(1)
        scroll_box = None
        try:
            scroll_box = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "xyi19xy.x1ccrb07.xtf3nb5.x1pc53ja.x1lliihq.x1iyjqo2.xs83m0k.xz65tgg.x1rife3k.x1n2onr6")))
            last_height, new_height = 0, 1
            scroll_attempts = 0
            max_scroll_attempts = 250  # Max attempts to avoid infinite loop
            w = 1
            while last_height != new_height and scroll_attempts < max_scroll_attempts:
                last_height = new_height
                sleep(0.5+1/w)
                new_height = self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight); return arguments[0].scrollHeight;", scroll_box)
                scroll_attempts += 1
                w += 1                 
                # Check if there are new elements loaded
                if last_height == new_height:
                    sleep(2.5)  # Wait a bit longer to ensure all elements are loaded
                    new_height = self.driver.execute_script(
                        "arguments[0].scrollTo(0, arguments[0].scrollHeight); return arguments[0].scrollHeight;", scroll_box)
                    if last_height == new_height:
                        sleep(2.5)  # Wait a bit longer to ensure all elements are loaded
                        new_height = self.driver.execute_script(
                            "arguments[0].scrollTo(0, arguments[0].scrollHeight); return arguments[0].scrollHeight;", scroll_box)
                        if last_height == new_height:
                            break  # No new elements loaded, exit loop
                        
            # Get people by anchor elements
            links = scroll_box.find_elements(By.TAG_NAME, 'a')
            names = [name.text for name in links if name.text != '']
            print(f"Got list of {len(names)} people from {list_type}.")
            return names

        except TimeoutException as e:
            print(f"Error: Timeout while waiting for the scrollable element. Please check if the class name has changed.")
            return []
        except Exception as e:
            print(f"Unhandled exception: {str(e)}")
            return []

    def close_browser(self):
        if self.driver is not None:
            self.driver.quit()

# Entry point
print("Instagram Unfollow-Checker")
bot = InstaUnfollowers()
try:
    bot.start_browser()  # Start the browser and login visibly
    unfollowers = bot.get_unfollowers()
    wb = Workbook()
    sheet = wb.active
    urls = []
    for i in range(0, len(unfollowers)):
        name = unfollowers[i].split("\n")[0]
        url = "https://instagram.com/" + name + "/"
        sheet.cell(row=i+1, column=1).value = '=HYPERLINK("{}", "{}")'.format(url, name)
        urls.append(url)
    wb.save("Unfollowers.xlsx")
finally:
    bot.close_browser()
