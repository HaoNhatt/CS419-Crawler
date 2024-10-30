import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


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

    def StartCrawling(self):
        self.__Crawl_Categories()

        print(self.category_links)
        self.__Crawl_Post_From_Category(self.category_links[1])
        # for category_link in self.category_links:
        #     print(f"Current category: {category_link}")
        #     self.__Crawl_Post_From_Category(category_link)

        #     time.sleep(1)

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

    def __Crawl_Post_From_Category(self, page_link):
        self.driver.get(page_link)
        self.driver.maximize_window()

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
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "div.item-related > div.box-category-item > a.box-category-link-with-avatar",
                    )
                )
            )
        except TimeoutException:
            print("Timeout: Unable to find news posts.")

        # Find all post elements
        # Since the first one and it related posts is outside the list, we handle it differently
        first_post = self.driver.find_element(
            By.CSS_SELECTOR,
            "div.item-first > a.box-category-link-with-avatar",
        )
        print(first_post.get_attribute("href"))

        # Related posts
        related_posts = self.driver.find_elements(
            By.CSS_SELECTOR,
            "div.item-related > div.box-category-item > a.box-category-link-with-avatar",
        )
        for post in related_posts:
            print(post.get_attribute("href"))

        self.__Crawl_Content_From_Post(first_post.get_attribute("href"))

        # posts = self.driver.find_elements(
        #     By.CSS_SELECTOR, "div.news-list.news-list-vertical > article"
        # )
        # for post in posts:
        #     # Extract post information
        #     post_title = post.find_element(By.CSS_SELECTOR, "h2 > a").text
        #     post_link = post.find_element(By.CSS_SELECTOR, "h2 > a").get_attribute(
        #         "href"
        #     )
        #     print(f"  Post: {post_title} - Link: {post_link}")

        #     # Navigate to the post page
        #     self.driver.get(post_link)

        # pass

    def __Crawl_Content_From_Post(self, post_link):
        self.driver.get(post_link)

        try:
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "h1.detail-title.article-title")
                )
            )

        except TimeoutException:
            print("Timeout: Unable to find heading.")

        title = self.driver.find_element(
            By.CSS_SELECTOR, "h1.detail-title.article-title"
        )
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

        print(f"Title: {title.text}")
        print(f"Category: {category.text}")
        print(f"Date: {date.text}")
        print(f"Author: {author.text}")
        print(f"Detail Sapo: {detail_sapo.text}")
        print("Main content:")
        for content in detail_content_text:
            print(f"\t - {content.text}")

        # Check if the post exist any comment section or not
        comment_section = self.driver.find_element(By.CSS_SELECTOR, ".detail_comment")
        if len(comment_section) == 0:
            print("This post don't have comment section")
        else:
            no_comment_element = self.driver.find_element(
                By.CSS_SELECTOR, ".text-no-comment"
            )
            has_comment_section = len(no_comment_element) == 0
            if has_comment_section:
                comments = comment_section.find_elements(By.CSS_SELECTOR, ".listcm")
            else:
                print("No comments found for this post yet.")

    # os.environ["PATH"] += r""

    # elements = driver.find_elements(By.CLASS_NAME, "box-category-item")
    # print(elements)
