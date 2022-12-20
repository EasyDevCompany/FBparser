import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'
}





def search_location_setup(driver, location):
    while len(driver.find_elements(By.XPATH, '//div[@class="x1iyjqo2"]//ancestor::div[@role="button"]'))==0:
        pass
    driver.find_element(By.XPATH, '//div[@class="x1iyjqo2"]//ancestor::div[@role="button"]').click()
    while len(driver.find_elements(By.XPATH, '//input[@aria-label="Укажите город"]'))==0:
        pass
    driver.find_element(By.XPATH, '//input[@aria-label="Укажите город"]').send_keys(location)
    while len(driver.find_elements(By.XPATH, '//li[@class="xh8yej3" and @role="option"]'))==0:
        pass
    driver.find_elements(By.XPATH, '//div[@class="x1lq5wgf xgqcy7u x30kzoy x9jhf4c x1lliihq"]')[0].click()
    driver.find_element(By.XPATH, '//div[@aria-label="Применить"]').click()



def scroll_to_the_end_of_page(driver):
    while True:
        end_check_list = driver.find_elements(
            By.XPATH, "//*[text()='Результаты из других категорий']")
        if len(end_check_list) > 0:
            break
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)


def login(driver, url):
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')

    driver.get(url)
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(username)
    driver.find_element(By.XPATH, '//*[@id="pass"]').send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="loginbutton"]').click()


def get_goods_links_from_page(driver):
    
    all_goods_container = driver.find_element(
        By.CSS_SELECTOR, '.x1xfsgkm > div:nth-child(1) > div:nth-child(2)')
    goods_containers = all_goods_container.find_elements(By.XPATH, '*')

    # delete all empty elements
    i = len(goods_containers)-1
    while len(goods_containers[i].find_elements(By.CLASS_NAME, 'xjp7ctv')) == 0:
        goods_containers.pop(i)
        i -= 1

    links = [container.find_element(By.TAG_NAME, 'a'
    ).get_attribute('href') for container in goods_containers]
    return links


def get_goods_data(links, driver):
    data = []
    for link in links:
        driver.get(link)
        while len(driver.find_elements(By.XPATH, '//div[@class="xyamay9 x1pi30zi x18d9i69 x1swvt13"]'))==0:
            pass
        name_price_container = driver.find_element(By.XPATH, '//div[@class="xyamay9 x1pi30zi x18d9i69 x1swvt13"]')
        name = name_price_container.find_element(By.XPATH, '//h1/span').text
        images_links = get_all_goods_images_links(driver)
        price = name_price_container.find_element(By.XPATH, '//div[@class="x1xmf6yo"]').find_element(By.XPATH, '//div/span').text
        real_estate_info = get_real_estate_info(driver)
        location = get_good_location(driver)
        # Getting full description
        if len(driver.find_elements(By.XPATH, '//span[text()="Ещё"]')) > 0: 
            driver.find_element(By.XPATH, '//span[text()="Ещё"]').click()
        if len(driver.find_elements(
            By.XPATH, '//div[@class="x14vqqas"]/preceding-sibling::span')) != 0:
            description = driver.find_element(
                By.XPATH, '//div[@class="x14vqqas"]/preceding-sibling::span').text
        else:
            description = ''
        saler_link = get_saler_link(driver)
        data.append({
            'good_link': link,
            'name': name,
            'images': images_links,
            'price': price,
            'real_estate_info': real_estate_info,
            'location': location,
            'description': description,
            'saler_link': saler_link
        })
    return data


def get_all_goods_images_links(driver):
    images_links = []
    images_container = driver.find_elements(
        By.XPATH, '//div[@class="x1a0syf3 x1ja2u2z"]/div')
    if len(images_container)==0:
        while len(driver.find_elements(By.XPATH, '//span[@class="x78zum5 x1vjfegm"]/descendant::img'))==0:
            pass
        return [driver.find_element(By.XPATH, '//span[@class="x78zum5 x1vjfegm"]/descendant::img').get_attribute('src')]
    for image_container in images_container[0].find_elements(By.XPATH, '*'):
        images_links.append(image_container.find_element(By.TAG_NAME, 'img').get_attribute('src'))

    return images_links
    

def get_real_estate_info(driver):
    real_estate_info = []
    flag = False
    separator = driver.find_elements(By.XPATH, "//*[contains(text(), 'Информация о недвижимости')]")
    if len(separator) == 0:
        return []

    container = driver.find_element(
        By.CSS_SELECTOR, 'div.xwib8y2:nth-child(6)')
    for div in container.find_elements(By.XPATH, '*'):
        if flag:
            real_estate_info.append(div.find_element(By.TAG_NAME, 'span').text)
        if len(div.find_elements(By.XPATH, "//*[contains(text(), 'Информация о недвижимости')]")) > 0:
            flag = True
    return real_estate_info


def get_good_location(driver):
    location_url = driver.find_element(By.XPATH,
    '//div[@class="x71s49j x10l6tqk x70y0r9 xmbx2d0"]//preceding-sibling::div').get_attribute('style')
    location_url.find('center')
    location_url = location_url[location_url.rfind('center')+7::]
    coordinates = location_url[:location_url.find('&'):].split(sep='%2C')
    return coordinates


def get_saler_link(driver):
    driver.find_element(
        By.XPATH, '//span[text()="Информация о продавце" and @class="x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft"]').click()
    while True:
        link = driver.find_elements(By.XPATH, '//a[@aria-label="Смотреть профиль"]')
        if len(link) > 0:
            return link[0].get_attribute('href')


def main(query, location):
    options = webdriver.FirefoxOptions()
    options.set_preference('general.useragent.override','Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0')
    options.set_preference('dom.webdriver.enabled', False)
    options.headless = True
    driver = webdriver.Firefox(options=options)
    load_dotenv()
    url = f'https://www.facebook.com/marketplace/112306758786227/search/?query={query}&exact=false'
    login(driver, url)
    search_location_setup(driver, location)
    scroll_to_the_end_of_page(driver)
    links = get_goods_links_from_page(driver)
    result = get_goods_data(links, driver)
    print(result)

if __name__ == '__main__':
    main(query='rent%20apartment', location='Лондон')
