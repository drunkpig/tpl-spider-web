from bs4 import BeautifulSoup
import json

with open("a.html", "r", encoding='utf-8') as f, open("lang_info.json", "w", encoding='utf-8') as f2:
    ctx  = f.readlines()
    content = "".join(ctx)
    soup = BeautifulSoup(content, "lxml")
    els = soup.find_all("a")
    datas = {}
    for a in els:
        lang_code = a.get("data-countryiso")
        lang_name = a.get("data-countryname")
        image = a.find("img")
        src_data = image.get("src")
        data = {
            "lang_code":lang_code,
            "lang_name":lang_name,
            "image_b64":src_data
        }
        datas[lang_code] = data

        print(json.dumps(data))
    f2.write(f"{json.dumps(datas)}\n")
