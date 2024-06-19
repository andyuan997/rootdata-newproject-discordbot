import requests
from bs4 import BeautifulSoup
import json
import os
from opencc import OpenCC

last_project = {}

def convert_simplified_to_traditional(simplified_text):
    cc = OpenCC('s2t')
    return cc.convert(simplified_text)

def save_project_to_file(project, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(project, f, ensure_ascii=False, indent=4)

def load_project_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def rootdata():

    url = 'https://www.rootdata.com/zh/Projects'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
    }

    # 發起GET請求
    response = requests.get(url, headers=headers)

    # 檢查請求是否成功
    if response.status_code != 200:
        print(f"請求失敗，狀態碼: {response.status_code}")
        return

    # 使用 BeautifulSoup 解析 HTML 內容
    soup = BeautifulSoup(response.content, 'html.parser')

    # 查找包含項目數據的HTML元素
    projects = {}
    project_rows = soup.find_all('tr', role='row')

    for row in project_rows:
        title_tag = row.find('a', class_='list_name')
        if title_tag:
            title = title_tag.text.strip()
            url = title_tag['href']
            full_url = f"https://www.rootdata.com{url}"

            tag_div = row.find('div', class_='tag_list')
            tags = tag_div.text.strip() if tag_div else '無'

            intro_span = row.find('span', class_='intro')
            intro = intro_span.text.strip() if intro_span else '無'

            projects[title] = {
                'url': full_url,
                'tags': tags,
                'intro': intro
            }

    # 反轉字典
    reversed_projects = {k: projects[k] for k in reversed(list(projects))}

    return reversed_projects

def send_to_discord(webhook_url, message):
    data = {
        "content": message
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("消息已成功發送到Discord")
    else:
        print(f"發送到Discord失敗，狀態碼: {response.status_code}")

def main():
    global last_project

    # Discord Webhook URL
    webhook_url = "Discord Webhook URL"

    last_project = load_project_from_file('last_project.json')

    now_project = rootdata()

    # 比較兩個字典，找出新增的文章
    new_articles = {k: v for k, v in now_project.items() if k not in last_project}

    # 如果有新的文章，發送到Discord
    for title, data in new_articles.items():
        message = f"[📢]({data['url']})  {title}：{convert_simplified_to_traditional(data['intro'])}\n類別：{convert_simplified_to_traditional(data['tags'])}"
        send_to_discord(webhook_url, message)

    # 更新last_project並保存到文件
    last_project = now_project
    save_project_to_file(last_project, 'last_project.json')

if __name__ == "__main__":
    main()
