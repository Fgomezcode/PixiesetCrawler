import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os

####
# LINK TO IMAGES GOES IN HERE!
#########################
# should be in the following format: https://[[domain]].pixieset.com/[[path]]
# LINK_TO_GALLERY = https://example.pixieset.com/name123123

# Your link should go inside the parentheses
LINK_TO_GALLERY = "https://www.example.com/"

###################################


# Function to scroll to the bottom of the page and ensure all dynamic content is loaded
def smart_scroll(driver):
    # the height of the current page
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page - can shorten this to make process faster but risk not loading all images
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        # if the new height has not changed, the bot is at the bottom of the page and all images
        # should have loaded and become visible.
        if new_height == last_height:
            # Try scrolling a bit up and down to trigger lazy loading elements, if any
            driver.execute_script("window.scrollBy(0, -100);")
            time.sleep(1) # wait one second to see if more images load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Check if new content was loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # If no new content, exit loop
        last_height = new_height


# Initialize Selenium WebDriver
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)



driver.get(LINK_TO_GALLERY)

# Smart scrolling to load all images
smart_scroll(driver)

# Find all images and elements with background images after full page load
images = driver.find_elements(By.TAG_NAME, "img")
background_elements = driver.find_elements(By.XPATH, "//*[contains(@style, 'background-image')]")




# Directory for images
images_dir = "downloaded_images"
os.makedirs(images_dir, exist_ok = True)

# Function to download an image
def download_image(image_url, destination_folder, index):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            file_path = os.path.join(destination_folder, f"image_{index}.jpg")
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {image_url} as {file_path}")
    except Exception as e:
        print(f"Failed to download {image_url}: {e}")


# Download images found in <img> tags
for index, image in enumerate(images):
    src = image.get_attribute('src')
    if src:
        download_image(src, images_dir, index)

# Download images from CSS background-images
for index, element in enumerate(background_elements, start = len(images)):
    style = element.get_attribute('style')
    if "background-image" in style:
        url_start = style.find("url(") + 4
        url_end = style.find(")", url_start)
        src = style[url_start:url_end].replace('"', '').replace("'", "")
        if src.startswith("http"):  # Ensure it's a valid URL
            download_image(src, images_dir, index + len(images))

# Clean up by closing the Selenium driver
driver.quit()
