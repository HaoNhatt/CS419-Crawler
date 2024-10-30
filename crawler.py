import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
from urllib.parse import urlparse
import time
import json


class Crawler:
    def __init__(
        self,
        baseURL="https://google.com",
        wait_time=5,
        executable_path="chromedriver.exe",
    ):
        self.baseURL = baseURL
        self.wait_time = wait_time
        self.service = Service(executable_path=executable_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.category_links = []
        self.post_link_queue = []
        self.crawled_posts = []

    def StartCrawling(self):
        self.__Crawl_Categories()

        print(self.category_links)
        self.__Crawl_Post_From_Category(self.category_links[1])
        # for category_link in self.category_links:
        #     print(f"Current category: {category_link}")
        #     self.__Crawl_Post_From_Category(category_link)

        #     time.sleep(1)

        self.driver.quit()

    def CustomCrawling(self):
        start_index = 0
        while True:
            user_input_link = input(
                "Type the URL or the category you want to crawl (type exit/quit/bye to cancel): "
            )

            if user_input_link.lower() in ["exit", "quit", "bye"]:
                break

            # user_input_number = input("How many post you want to crawl: ")

            self.__Crawl_Post_From_Category(user_input_link, start_index)
            start_index += 24

        self.driver.quit()

    def __Crawl_Categories(self):
        self.driver.get(self.baseURL)

        # Wait for the page to load up necessary elements
        try:
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".header__nav-flex > .menu-nav > li > .nav-link")
                )
            )
        except TimeoutException:
            print("Timeout: Unable to find category bar.")

        # Get all the categories
        category_elements = self.driver.find_elements(
            By.CSS_SELECTOR, ".header__nav-flex > .menu-nav > li > .nav-link"
        )

        for category_element in category_elements:
            category_link = category_element.get_attribute("href")
            if category_link == self.baseURL:
                continue
            # category_name = category_element.text
            self.category_links.append(category_link)

    def __Crawl_Post_From_Category(self, page_link, start_index=0):
        if not self.is_valid_url(page_link):
            print("You entered an invalid URL, please try again")
            return

        self.post_link_queue = []
        self.crawled_posts = []

        self.driver.get(page_link)
        self.driver.maximize_window()

        try:
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div#IconLoadListDetail",
                    )
                )
            )
        except TimeoutException:
            print("Timeout: Unable to find news posts.")

        self.driver.execute_script(
            "arguments[0].scrollIntoView();",
            self.driver.find_element(By.CSS_SELECTOR, "div#IconLoadListDetail"),
        )
        time.sleep(5)

        # Wait for the elements to load up (the first element)
        try:
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.item-first > a.box-category-link-with-avatar",
                    )
                )
            )
            # WebDriverWait(self.driver, self.wait_time).until(
            #     EC.presence_of_all_elements_located(
            #         (
            #             By.CSS_SELECTOR,
            #             "div.item-related > div.box-category-item > a.box-category-link-with-avatar",
            #         )
            #     )
            # )
            # WebDriverWait(self.driver, self.wait_time).until(
            #     EC.presence_of_all_elements_located(
            #         (
            #             By.CSS_SELECTOR,
            #             "div#load-list-news > div.box-category-item > a",
            #         )
            #     )
            # )
        except TimeoutException:
            print("Timeout: Unable to find news posts.")

        # Find all post elements
        # Since the first one and it related posts is outside the list, we handle it differently
        first_post = self.driver.find_element(
            By.CSS_SELECTOR,
            "div.item-first > a.box-category-link-with-avatar",
        )
        print(first_post.get_attribute("href"))
        self.post_link_queue.append(first_post.get_attribute("href"))

        # Related posts
        related_posts = self.driver.find_elements(
            By.CSS_SELECTOR,
            "div.item-related > div.box-category-item > a.box-category-link-with-avatar",
        )
        for post in related_posts:
            print(post.get_attribute("href"))
            self.post_link_queue.append(post.get_attribute("href"))

        list_posts = self.driver.find_elements(
            By.CSS_SELECTOR,
            "div#load-list-news > div.box-category-item > a",
        )
        for post in list_posts:
            print(post.get_attribute("href"))
            self.post_link_queue.append(post.get_attribute("href"))

        print(len(self.post_link_queue))

        for post in self.post_link_queue:
            self.__Crawl_Content_From_Post(post, start_index)

        # self.__Crawl_Content_From_Post(first_post.get_attribute("href"))
        # self.__Crawl_Content_From_Post(
        #     "https://tuoitre.vn/dang-doi-moi-dua-dat-nuoc-vuon-minh-ro-nguoi-ro-viec-ro-trach-nhiem-20241030112821598.htm"
        # )
        # self.__Crawl_Content_From_Post(
        #     "https://tuoitre.vn/xu-ly-vi-pham-giao-thong-hoc-sinh-nguoi-lon-doi-mu-bao-hiem-cho-minh-nhung-bo-quen-con-tre-20241030092818449.htm"
        # )

    def __Crawl_Content_From_Post(self, post_link, start_index=0):
        self.driver.get(post_link)

        try:
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "h1.detail-title.article-title")
                )
            )
        except TimeoutException:
            print("Timeout: Unable to find heading.")

        post_id = len(self.crawled_posts) + start_index
        title = self.driver.find_element(By.CSS_SELECTOR, "h1.detail-title")
        category = self.driver.find_element(By.CSS_SELECTOR, "div.detail-cate > a")
        date = self.driver.find_element(By.CSS_SELECTOR, "div.detail-time > div")
        author = self.driver.find_element(By.CSS_SELECTOR, "div.author-info > a")
        detail_sapo = self.driver.find_element(By.CSS_SELECTOR, "h2.detail-sapo")
        content_div = self.driver.find_element(
            By.CSS_SELECTOR, "div.detail-content.afcbc-body"
        )
        detail_content_text = content_div.find_elements(
            By.XPATH, "./*[self::p or self::h2]"
        )
        content = []
        for content_text in detail_content_text:
            content.append(content_text.text)
        audio = ""
        if len(self.driver.find_elements(By.CSS_SELECTOR, "audio.vjs-tech")):
            audio = self.driver.find_element(
                By.CSS_SELECTOR, "audio.vjs-tech"
            ).get_attribute("src")
        imgs = self.driver.find_elements(
            By.CSS_SELECTOR,
            ".VCSortableInPreviewMode > div > a, .VCSortableInPreviewMode > figure > a",
        )
        img_urls = []
        for img in imgs:
            img_urls.append(img.get_attribute("href"))

        post = {
            "postID": post_id,
            "Title": title.text,
            "Category": category.text,
            "Date": date.text,
            "Author": author.text,
            "Detail_sapo": detail_sapo.text,
            "Content": content,
            "Audio": audio,
            "Img": img_urls,
        }

        self.crawled_posts.append(post)

        print(self.crawled_posts)

        self.__export_json(post)
        for img in post["Img"]:
            self.__Save_Image(image_url=img, post_id=post["postID"])
        self.__Save_Audio(audio_url=post["Audio"], post_id=post["postID"])

        time.sleep(1)

        # print(f"Title: {title.text}")
        # print(f"Category: {category.text}")
        # print(f"Date: {date.text}")
        # print(f"Author: {author.text}")
        # print(f"Detail Sapo: {detail_sapo.text}")
        # print("Main content:")
        # for content in detail_content_text:
        #     print(f"\t - {content.text}")
        # print(f"Audio src: {audio.get_attribute("src")}")
        # for img in imgs:
        #     print(f"Img link: {img.get_attribute("href")}")

        # Check if the post exist any comment section or not

        # comment_section = self.driver.find_elements(By.CSS_SELECTOR, "#detail_comment")
        # if len(comment_section) == 0:
        #     print("This post don't have comment section")
        # else:
        #     try:
        #         WebDriverWait(self.driver, self.wait_time).until(
        #             EC.presence_of_all_elements_located(
        #                 (By.CSS_SELECTOR, "li.item-comment")
        #             )
        #         )
        #     except TimeoutException:
        #         print("Timeout: Unable to find comments.")

        #     comments = self.driver.find_elements(By.CSS_SELECTOR, "li.item-comment")
        #     if len(comments):
        #         print(f"This post has comments: {len(comments)}")
        #         self.driver.execute_script(
        #             "arguments[0].scrollIntoView();",
        #             self.driver.find_element(By.CSS_SELECTOR, ".detail-tab"),
        #         )
        #         try:
        #             WebDriverWait(self.driver, self.wait_time).until(
        #                 EC.element_to_be_clickable(
        #                     (By.CSS_SELECTOR, "button.commentpopupall")
        #                 )
        #             )
        #             # print("button found")
        #         except TimeoutException:
        #             print("Timeout: Unable to find comments.")

        #         expand_comment_element = self.driver.find_element(
        #             By.CSS_SELECTOR, "button.commentpopupall"
        #         )

        #         time.sleep(3)
        #         expand_comment_element.click()
        #         time.sleep(3)

        #     else:
        #         print("No comments found for this post yet.")

    def __Save_Image(self, image_url, post_id):
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Get the file extension
            image_extension = urlparse(image_url).path.split(".")[-1]
            image_name = urlparse(image_url).path.split("/")[-1]

            # Create the image directory if it doesn't exist
            image_dir = f"images/{post_id}"
            os.makedirs(image_dir, exist_ok=True)

            # Save the image
            with open(f"{image_dir}/{image_name}.{image_extension}", "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded image: {image_name}.{image_extension}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")

    def __Save_Audio(self, audio_url, post_id):
        try:
            if audio_url == "":
                return
            response = requests.get(audio_url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Get the file extension
            audio_extension = urlparse(audio_url).path.split(".")[-1]

            # Create the audio directory if it doesn't exist
            audio_dir = "audio"
            os.makedirs(audio_dir, exist_ok=True)

            # Save the audio file
            with open(f"{audio_dir}/{post_id}.{audio_extension}", "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded audio: {post_id}.{audio_extension}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading audio: {e}")

    def is_valid_url(self, url):
        try:
            response = requests.head(url)
            if response.status_code in range(200, 300):
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return False

    def __export_json(self, post_data):
        try:
            # Create the 'data' folder if it doesn't exist
            os.makedirs("data", exist_ok=True)

            # Construct the JSON file path
            json_file_path = f"data/{post_data["postID"]}.json"

            # Write the data to the JSON file
            with open(json_file_path, "w", encoding="utf-8") as file:
                json.dump(
                    post_data, file, indent=4, ensure_ascii=False
                )  # Indent the output for readability
            print(f"Data exported to: {json_file_path}")

        except Exception as e:
            print(f"Error exporting data to JSON: {e}")
