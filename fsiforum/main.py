# STANDARD LIBS
import os
import re
import argparse

from urllib.request import urlretrieve

# PIP LIBS
import requests
from bs4 import BeautifulSoup

COOKIES = {
    "PHPSESSID": None,
    "__utma": "67084473.1061214629.1638632943.1638632943.1638632943.1",
    "__utmc": "67084473",
    "__utmz": "67084473.1638632943.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
    "phpbb3_5cvtp_u": "1",
    "phpbb3_5cvtp_k": "",
    "phpbb3_5cvtp_sid": "6bc2505567269f5517f3f91332b14d1d",
    "style_cookie": "null",
    "__utmt": "1",
    "__utmb": "67084473.30.10.1638632943",
}

HEADERS = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Referer": "http://fsiforum.cz/upload/index.php",
    "Accept-Language": "cs-CZ,cs;q=0.9,sk;q=0.8",
}

page_count = 0
file_count = 0
transfered = 0
log_file = None


class File:
    def __init__(self, url, name):
        self.url = url
        pre, ext = os.path.splitext(name)

        self.name = name if ext != "" else name + ".file"


class Page:
    def __init__(self, url, path):
        self.url = url
        self.path = path
        self.pages = []
        self.files = []

    def scrape(self):
        if self.url != "":
            params = (("dir", self.url),)
        else:
            params = ()

        response = requests.get(
            "http://fsiforum.cz/upload/index.php",
            headers=HEADERS,
            params=params,
            cookies=COOKIES,
            verify=False,
        ).content

        soup = BeautifulSoup(response, "html.parser", from_encoding="utf-8")
        global page_count
        global file_count

        if soup.select('label[class*="login"]'):
            print("Wrong session (user is not logged in).")
            return

        for link in soup.select('tr[class*="dir"]'):
            size = link.find("td", {"class": "size"}).text

            data = link.find("td", {"class": "name"}).find("a")
            href = data.get("href").replace("index.php?dir=", "").replace("%2F", "/")
            title = "".join(
                [
                    c
                    for c in data.text
                    if c.isalpha() or c.isdigit() or c == " " or c == "-" or c == "_"
                ]
            ).rstrip()

            if size == "0 soubory":
                print("Skipping empty folder: {}".format(os.path.join(self.path, title)))
                continue

            self.pages.append(Page(href, os.path.join(self.path, title)))
            page_count += 1

        for link in soup.select('tr[class*="file"]'):
            data = link.find("td", {"class": "name"}).find("a")
            href = data.get("href")
            title = "".join(
                [
                    c
                    for c in data.text
                    if c.isalpha()
                    or c.isdigit()
                    or c == " "
                    or c == "."
                    or c == "-"
                    or c == "_"
                ]
            ).rstrip()
            
            title = re.sub(r"\.+", ".", title)
            
            self.files.append(File(href, title))

            file_count += 1

        # print("Scraped: {}, found {} pages and {} files".format(self.url, len(self.pages), len(self.files)))

        for page in self.pages:
            page.scrape()

    def download(self, diff, log, text_only):
        global log_file
        global transfered

        for file in self.files:
            file_path = os.path.join(self.path, file.name)
            file_path = file_path.replace(" .", ".")

            if diff and os.path.isfile(file_path):
                continue
            
            if not text_only:
                path_parts = self.path.split("/")
                create_path = ""

                for part in path_parts:
                    create_path = os.path.join(create_path, part)

                    if not os.path.exists(create_path):
                        os.makedirs(create_path, exist_ok=True)

            if log or text_only:
                log_file.write('"{url}" "{path}"\n'.format(url=file.url, path=file_path))

            if not text_only:
                print("saving {} to {}".format(file.name, os.path.abspath(file_path)))
                try:
                    urlretrieve("http://fsiforum.cz/upload/" + file.url, file_path)
                    transfered += os.path.getsize(file_path)
                except Exception as e:
                    print("Download for file {} failed: {}".format(file_path, e))
            else:
                print("Logged file {}".format(file_path))

        for page in self.pages:
            page.download(diff, log, text_only)

    def __str__(self):
        return f'<class="Page" url="{self.url}" path="{self.path}" pages="{self.pages}" files="{self.files}">'


def main():
    parser = argparse.ArgumentParser(description="FSI Forum Scraper")

    parser.add_argument("--stats", action="store_true", dest="stats")
    parser.add_argument("--diff", action="store_true", dest="diff")
    parser.add_argument("--log", action="store_true", dest="log")
    parser.add_argument("--text-only", action="store_true", dest="text_only")
    parser.add_argument("--session", action="store", dest="session")

    arguments = parser.parse_args()

    global COOKIES

    if arguments.session:
        COOKIES["PHPSESSID"] = arguments.session
    else:
        print("Missing paramater --session")
        return 1

    path = os.path.join(".", "index")

    if (
        not arguments.diff
        and not arguments.stats
        and not arguments.text_only
        and os.path.exists(path)
    ):
        print("There's already 'index' folder. Delete it or use --diff.")
        return 1

    index_page = Page("", path)
    index_page.scrape()

    print("Scraping done. Found {} pages and {} files".format(page_count, file_count))

    if arguments.stats:
        return 0

    if arguments.log or arguments.text_only:
        global log_file
        log_file = open("log.txt", "w", encoding="utf-8")

    index_page.download(arguments.diff, arguments.log, arguments.text_only)
    
    if log_file:
        log_file.close()

    print("Downloading finished. Downloaded {} files.".format(file_count))
