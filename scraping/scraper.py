import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import urllib.request
import ssl
import json
import pandas as pd

store_list = list(pd.read_excel('excel_files/store_list.xlsx')[0])

# [점] 으로 끝나지 않을 때, 대학로 붙이기
for i in range(len(store_list)):
    if store_list[i][-1] != "점":
        store_list[i] = store_list[i] + ' 대학로'

print(store_list)


def get_info(text):
    context = ssl._create_unverified_context()
    client_id = "iH4tSGNtmsLymwxh8TSh"
    client_secret = "4q6cF8VLNw"
    encText = urllib.parse.quote(text)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText + "&display=10&start=1&sort=sim"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request, context=context)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        res = response_body.decode('utf-8')
    else:
        print("Error Code:" + rescode)

    data = json.loads(res)

    # print(res)

    link_list = []
    for head in data["items"]:
        link_list.append(head['link'])

    return link_list


ttl_list = []
for store_name in store_list:
    url_list = get_info(store_name)
    ttl_list.append([store_name, url_list])
print(ttl_list)


# iframe 제거
def delete_iframe(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()  # 문제시 프로그램 종료
    soup = BeautifulSoup(res.text, "lxml")

    try:
        src_url = "https://blog.naver.com/" + soup.iframe["src"]
    except:
        src_url = url

    return src_url


# 본문 스크래핑
def text_scraping(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
        res = requests.get(url, headers=headers)
        res.raise_for_status()  # 문제시 프로그램 종료
        soup = BeautifulSoup(res.text, "lxml")

        if soup.find("div", attrs={"class": "se-main-container"}):
            text = soup.find("div", attrs={"class": "se-main-container"}).get_text()
            text = text.replace("\n", "")  # 공백 제거
            # print("블로그")
            return text
        else:
            return ""
    except:
        return ""


# 크롤링 실행
result = []
for i in range(len(ttl_list)):
    store = ttl_list[i][0]
    url_list = ttl_list[i][1]
    contents_soup = ''

    for url in url_list:
        contents_soup += text_scraping(delete_iframe(url))
    result.append([store, contents_soup])
    print('{}/{}...crawling...{}'.format(i + 1, len(ttl_list), contents_soup))

dummy_data = pd.DataFrame(result, columns=['store', 'bow'])
dummy_data.to_excel('excel_files/dummy_data.xlsx', index=False)
