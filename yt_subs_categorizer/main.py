#!/bin/env python3

import re
import csv
import typing

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.options import Options


def get_element(driver: webdriver.firefox.webdriver.WebDriver, locator: str, timeout=60):
    try:
        result = ui.WebDriverWait(driver, timeout).until(EC
                                                         .presence_of_element_located
                                                         ((By.
                                                           XPATH,
                                                           locator)))
        if "\n" in result.text:
            result.click()
            return get_element(driver, locator)
        elif "Category" in result.text:
            return result.text.split(':')[1].strip()
        elif "Show More" in result.text:
            return "DELETED"
        else:
            return "Error"

    except TimeoutException:
        return "Connection timeout"
    except NoSuchElementException:
        return False


def scrape(f: typing.TextIO, o: typing.TextIO, driver: webdriver.firefox.webdriver.WebDriver):
    BASE_URL = "http://www.youtube.com/"
    # INVIDIOUS_URL = "https://yewtu.be/"
    PIPED_URL = "https://piped.video/"
    EXPATH = '/html/body/div/div/div/button[contains(text(), "Show More")] |\
              //div[@class=\"video-grid\"]/div[1]/a |\
              //div[contains(text(), "Category")]'

    for i, row in enumerate(csv.reader(f, delimiter=',')):
        if not len(row) or i == 0: continue
        print(f"Current line: {i}")

        id, url, title = row
        new_url = (re.sub(BASE_URL, PIPED_URL, url))
        driver.get(new_url)

        result = get_element(driver, EXPATH)
        o.write(f"\"{id}\",\"{url}\",\"{title}\",\"{result}\"\n")


def main():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    with open('./subscriptions.csv', 'r') as f, open('./output.csv', 'w') as o:
        scrape(f, o, driver)
    driver.quit()


if __name__ == "__main__":
    main()
