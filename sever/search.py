import json
import requests
from lxml import etree

def search_so(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    }
    response = requests.get(f'https://www.so.com/s?q={query}', headers=headers)

    r = response.text
    html = etree.HTML(r, etree.HTMLParser())
    r1 = html.xpath('//h3[@class="res-title"]/a')
    r2 = html.xpath('//p[@class="res-desc"]')
    r3 = html.xpath('//h3[@class="res-title"]/a/@href')

    # 取最小长度，以避免索引越界
    min_length = min(len(r1), len(r3),len(r2))  # 移除 r2 的依赖，因为可能存在没有摘要的情况

    results = []
    for i in range(min_length):
        title = r1[i].xpath('string(.)')
        url = r3[i]
        content = r2[i].xpath('string(.)')
        result = {"content": title+content, "url": url}
        results.append(result)
        print(title, end='\n')  # Optional: Print to console
        print(url, end='\n\n')  # Optional: Print to console

    # 保存结果到 JSON 文件
    with open('../process_data/search.json', 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

# 调用函数
#search_so('机器人')
