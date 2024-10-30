from crawler import Crawler

BaseURL = "https://tuoitre.vn/"
wait_time = 5


if __name__ == "__main__":
    crawler = Crawler(baseURL=BaseURL, wait_time=wait_time)
    crawler.StartCrawling()

    pass
