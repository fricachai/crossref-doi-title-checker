import re
import requests
from time import sleep

def normalize(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("’", "'").replace("–", "-").replace("—", "-")
    return s

def crossref_lookup(doi: str):
    url = f"https://api.crossref.org/works/{doi}"
    r = requests.get(url, timeout=20, headers={"User-Agent": "doi-check/1.0"})
    r.raise_for_status()
    msg = r.json()["message"]
    title = (msg.get("title") or [""])[0]
    journal = (msg.get("container-title") or [""])[0]

    year = None
    for k in ["published-print", "published-online", "created", "issued"]:
        if msg.get(k) and msg[k].get("date-parts"):
            year = msg[k]["date-parts"][0][0]
            break

    return {
        "doi": doi,
        "title": title,
        "journal": journal,
        "year": year,
    }

# 👇👇👇 就是這裡 👇👇👇
if __name__ == "__main__":
    dois = [
        "10.1016/j.compedu.2010.01.007",
        "10.1016/j.compedu.2010.02.007",
    ]

    for doi in dois:
        meta = crossref_lookup(doi)
        print(meta)
        sleep(0.2)
