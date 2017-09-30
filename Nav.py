# -*- coding: utf-8 -*-

import time
from bs4 import BeautifulSoup
from selenium import webdriver
import traceback
from pyquery import PyQuery as pq
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.PhantomJS(executable_path="C:/backup/Tools/phantomjs-2.1.1-windows/bin/phantomjs.exe",
                                 service_args=['--ssl-protocol=any'])
driver.maximize_window()
wait = WebDriverWait(driver, 10)

motorcycles_dropdown = "//a[@data-dropdown='motorcycles-dropdown']"
dropdown_close = 'global-navigation__menu-dropdown-close-button'
outputpath = 'C:/backup/motorcycles_1.txt'

CountryResultMessage = 'country match'
LanguageResultMessage = 'language match'
OldPatternMessage = 'match old country pattern'
MissMatchMessage = 'there is something doesn\'t correct'


def getPageSource(url, element, dropdown_close):
    driver.get(url)
    try:
        motorcycles = wait.until(
            EC.presence_of_element_located((By.XPATH, element))
        )
    except TimeoutException:
        traceback.print_exc()
    motorcycles.click()
    time.sleep(5)
    motor_dropdown_close = driver.find_element_by_class_name(dropdown_close)
    if motor_dropdown_close:
        print('motorcycles dropdown is opened')
        html = driver.page_source
        motorcycles_dropdown = pq(html)
    return motorcycles_dropdown


def getBikeLinks(html):
    bikelist = []
    items = html('.motorcycles-dropdown__motorcycle-panel').items()
    for item in items:
        bikeName = item.find('h5').text()
        bikePrice = item.find('p').text()
        CTALabel = item.find('a').text()
        CTALink = item.find('a').attr['href']
        bike = {'Name': bikeName, 'Price': bikePrice, 'CTALabel': CTALabel, 'CTALink': CTALink}
        bikelist.append(bike)
    return bikelist


def getLinks(html):
    dct = {}
    soup = BeautifulSoup(str(html), 'html.parser')
    a = soup.select('a[href]')
    for i in a:
        try:
            if ((i.attrs['href'] != '#') & (i.attrs['href'] != "") & (
                        i.attrs['href'] != "javascript:void(0)") & (i.attrs['href'] != "href")):
                href = i.attrs['href']
                linklabel = i.text.strip()
                dct[linklabel] = href
        except Exception as err:
            print(err)
            continue
    return dct


def generateURL(mapping_list):
    url_list = []
    host = 'https://motorcycles.harley-davidson.com/'
    #host = "http://119.9.126.75:8081/content/h-d/"
    for i in range(len(mapping_list)):
        if i % 2 == 0:
            print(mapping_list[i] + '/' + mapping_list[i + 1])
            url = host + mapping_list[i] + '/' + mapping_list[i + 1] + '/2018/index.html'
            url_list.append(url)
    return url_list


def urlParser(dct, country, language, oldPattern):
    for k in dct:
        parser = dct[k].split('/')
        outputFile(dct[k], outputpath)
        for i in parser:
            try:
                if(i==country):
                    print('country match')
                    outputFile(CountryResultMessage, outputpath)
                    continue
                elif(i==language):
                    print('language match')
                    outputFile(LanguageResultMessage, outputpath)
                elif(i==oldPattern):
                    print('match old country pattern')
                    outputFile(OldPatternMessage, outputpath)
                    break
            except Exception as err:
                print('Exception: ', err)


def outputFile(parserlist, outputpath):
    try:
        with open(outputpath, 'a') as f:
                f.write(parserlist + '\n')
    finally:
        f.close()


def main():
    mapping_list = ['us', 'en', 'ca', 'en']
    pages = generateURL(mapping_list)
    for page in pages:
        path = page.split('/')
        html = getPageSource(page, motorcycles_dropdown, dropdown_close)
        dct = getLinks(html)
        bikes = getBikeLinks(html)
        outputFile(
            '---------------------Start printing links in navigation,on locale ' + path[3] + '/' +
            path[4] + ' homepage---------------------------', outputpath)
        urlParser(dct, path[3], path[4], path[4] + '_' + path[3].upper())
        outputFile('---------------------Start printing bikes part -------------------------------', outputpath)
        for bike in bikes:
            outputFile(
                '---------------------This is ' + str(bikes.index(bike)) + '-------------------------------',
                outputpath)
            urlParser(bike, path[3], path[4], path[4] + '_' + path[3].upper())


if __name__ == '__main__':
    main()
