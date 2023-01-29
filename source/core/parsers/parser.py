import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from cattrs import structure

from .models import Data, Chapter


time_format = "%d.%m.%Y"
xpath = '//*[@id="main-page"]/div/div/div/div[2]/div[2]/div[3]/div/div[1]/div[1]/div[2]/div[{index}]'


def get_search_url(domain: str, title_name: str) -> str:
    return f"https://{domain}/manga-list?sort=rate&dir=desc&page=1&name={quote(title_name)}"


class Parser:
    def __init__(self, driver: webdriver.Chrome, domain: str) -> None:
        self.driver = driver
        self.domain = domain
        self.is_busy = False

    def get_title(self, name: str) -> Data | None:
        self.is_busy = True
        url = self.search_title(name)

        self.driver.get(url=url)

        # Getting data of manga
        data = {
            "name": self.driver.find_element(By.CLASS_NAME, "media-name__main").text,
            "url": url
        }

        image_card = self.driver.find_element(By.CLASS_NAME, "media-sidebar__cover")
        data["image_url"] = image_card.find_element(By.XPATH, "img").get_attribute("src")

        self.driver.get(url=f"{url}?section=chapters")

        last_chapter_data = self._get_latest_chapter()
        data["last_chapter"] = last_chapter_data

        self.is_busy = False
        return structure(data, Data)

    def search_title(self, name: str) -> str | None:
        self.driver.get(url=get_search_url(self.domain, name))
        try:
            url = self.driver.find_element(By.CLASS_NAME, "media-card").get_attribute("href")
        except NoSuchElementException:
            return

        return url

    def _get_latest_chapter(self) -> dict | None:
        try:
            chapter_data = self.driver.find_element(By.CLASS_NAME, "media-chapter")
            chapter_data = chapter_data.find_element(By.CLASS_NAME, "link-default")
            chapter_name = chapter_data.text.splitlines()
            if not chapter_name:
                return
            chapter_name = chapter_name[0]
            chapter_url = chapter_data.get_attribute("href")
        except NoSuchElementException:
            # Тайтл имеет несколько переводов, поэтому начальная страница пустая
            return self.get_chapter_from_team()

        return {"name": chapter_name, "url": chapter_url}

    def get_chapter_from_team(self):
        team_list = self.driver.find_element(By.CLASS_NAME, "team-list")
        teams: list[WebElement] = team_list.find_elements(
            By.CLASS_NAME, "team-list-item"
        )

        data = {}

        for i in range(len(teams)):
            team = team_list.find_element(
                By.XPATH, xpath.format(index=i + 1)
            )
            # Получаем элемент через XPATH, т.к. иначе на него нельзя нажать
            team.click()
            # Нажимаем, чтобы получить все части перевода от команды

            chapter = self._get_latest_team_chapter()
            chapter_url = chapter.find_element(
                By.CLASS_NAME, "link-default"
            ).get_attribute("href")
            chapter_data = chapter.text.splitlines()
            time = chapter_data[2]
            dtime = datetime.datetime.strptime(time, time_format)
            data[dtime] = {"name": chapter_data[0], "url": chapter_url}

        return self.filter_chapters_by_time(data)

    def _get_latest_team_chapter(self) -> WebElement:
        chapters = self.driver.find_elements(
            By.CLASS_NAME, "vue-recycle-scroller__item-view"
        )
        for chapter in chapters:
            attr = chapter.get_attribute("style")
            if attr == "transform: translateY(0px);":
                # Наговнокодили с фронтендом, а мне это парсить...
                # При переключении команд, предыдущие главы просто скрываются css свойством,
                # но они всё ещё присутствуют в списке, поэтому их надо отфильтровать
                return chapter.find_element(By.CLASS_NAME, "media-chapter")

    @staticmethod
    def filter_chapters_by_time(data: dict[datetime.datetime, dict[str, str]]):
        return data[max(data)]

    def get_latest_chapter(self, url: str) -> Chapter:
        if "section=chapters" not in url:
            url += "?section=chapters"

        self.driver.get(url)
        chapter_data = self._get_latest_chapter()

        return Chapter(**chapter_data)
