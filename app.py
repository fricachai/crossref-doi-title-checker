import streamlit as st
st.write("streamlit version:", st.__version__)

import requests
import re
from time import sleep

st.set_page_config(page_title="Crossref DOI Title Checker", layout="centered")

st.title("Crossref DOI Title Checker")
st.write("Paste DOIs below (one DOI per line), then click **Check**.")

def crossref_lookup(doi: str):
    url = f"https://api.crossref.org/works/{doi}"
    r = requests.get(url, timeout=20, headers={"User-Agent": "doi-title-checker"})
    r.raise_for_status()
    msg = r.json()["message"]
    title = (msg.get("title") or [""])[0]
    journal = (msg.get("container-title") or [""])[0]
    year = None
    for k in ["published-print", "published-online", "issued", "created"]:
        if msg.get(k) and msg[k].get("date-parts"):
            year = msg[k]["date-parts"][0][0]
            break
    return {
        "DOI": doi,
        "Title (Crossref)": title,
        "Journal": journal,
        "Year": year,
    }

# ===== 使用者輸入區 =====
doi_input = st.textarea(
    "DOIs",
    height=150,
    placeholder="10.1016/j.compedu.2010.01.007\n10.1016/j.compedu.2010.02.007"
)

# ===== 按鈕 =====
if st.button("Check DOIs"):
    dois = [d.strip() for d in doi_input.splitlines() if d.strip()]
    if not dois:
        st.warning("Please enter at least one DOI.")
    else:
        results = []
        with st.spinner("Querying Crossref..."):
            for doi in dois:
                try:
                    results.append(crossref_lookup(doi))
                    sleep(0.2)
                except Exception as e:
                    results.append({
                        "DOI": doi,
                        "Title (Crossref)": "ERROR",
                        "Journal": "",
                        "Year": "",
                    })
        st.success(f"Checked {len(results)} DOIs")
        st.dataframe(results, use_container_width=True)

