import requests
from bs4 import BeautifulSoup
import pandas as pd
import jieba

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

table01 = pd.DataFrame(columns=["Name_id", "Name", "Avg_score", "Effect"])
table02 = pd.DataFrame(columns=["Name_id", "Skin_type", "Score", "Age", "Content"])

def get_stock(url, ts, naid):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    name = soup.find("div", class_="review-title single-dot")
    table01.at[(naid - 1), "Name_id"] = naid
    table01.at[(naid - 1), "Name"] = name.text.split("] ")[1]
    
    
    idx = ts
    fu_age = soup.find_all("div", class_="author-review-status")
    for i in fu_age:
        table02.at[idx, "Skin_type"] = i.text.split("・")[0]
        table02.at[idx, "Age"] = i.text.split("・")[1]
        table02.at[idx, "Name_id"] = naid
        idx += 1

    idx = ts
    star = soup.find_all("div", class_="review-score")
    for i in star:
        table02.at[idx, "Score"] = i.text
        idx += 1
    sb = ""
    idx = ts
    info_links = soup.find_all("a", class_="review-content-top")
    for info_link in info_links:
        info_link = "https://www.cosme.net.tw" + info_link.get("href")
        res_info = requests.get(info_link, headers=HEADERS)
        soup_info = BeautifulSoup(res_info.text, "html.parser")
        content = soup_info.find("div", class_="review-content")
        for extract_tag in content.find_all("div", class_="review-attributes"):
            sg = extract_tag.extract()
            sb += sg.text.split("・")[1].replace(" ", "").replace("效果：", "").replace("--", "")
        table02.at[idx, "Content"] = content.text
        idx += 1
        print(f"page:{idx}")
    print(sb)

    next_link = soup.find("a", class_="next_page")
    return ("https://cosme.net.tw" + next_link.get("href")) if next_link != None else None



# jieba.load_userdict("mydict.txt")
def jb_sort(sb):
    word_cut_grt = jieba.cut(sb)
    word_cut_list = [
        w for w in word_cut_grt if len(w) > 1
    ]

    wd_dict = {}
    for wd in word_cut_list:
        if wd in wd_dict:
            wd_dict[wd] += 1
        else:
            wd_dict[wd] = 1

    wd_con_list = []
    for k, v in wd_dict.items():
        wd_con_list.append((k, v))
    wd_con_list.sort(key=lambda x: x[1], reverse=True)
    top5 = ""
    ts = 0
    for top in wd_con_list:
        if ts < 5:
            top5 += top[0] + "、"
            ts += 1
        else:
            top5 += top[0]
            break
    return top5



urls = (
    "https://www.cosme.net.tw/products/87330/reviews",
    "https://www.cosme.net.tw/products/87330/reviews"
)


naid = 1
for url in urls:
    ts = 0
    next_page = True
    while next_page != False:
        url = get_stock(url, ts, naid)
        print(url)
        ts += 15
        if url == None:
            break
    
    table02["Age"] = table02["Age"].apply(lambda x: x[0:2])
    table02["Content"] = table02["Content"].apply(lambda x: x.replace(" ", ""))
    table02.to_csv(f"table02_No{naid}.csv", index=False)

    table01.at[(naid - 1), "Avg_score"] = round(table02["Score"].astype(int).mean(), 2)
    naid += 1

table01.to_csv(f"table01.csv", index=False)
    
