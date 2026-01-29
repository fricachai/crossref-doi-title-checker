import streamlit as st
import re
import requests
from time import sleep

st.title("Crossref DOI Title Checker")

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
        "DOI": doi,
        "Title": title,
        "Journal": journal,
        "Year": year,
    }

dois = [
    "10.1016/j.compedu.2010.01.007",
    "10.1016/j.compedu.2010.02.007",
]

results = []

for doi in dois:
    results.append(crossref_lookup(doi))
    sleep(0.2)

st.dataframe(results)
