import streamlit as st
import requests
from time import sleep

# 1) set_page_config 必須放最上面（第一個 Streamlit 指令）
st.set_page_config(page_title="Crossref DOI Title Checker", layout="centered")

# （可選）版本顯示
st.write("streamlit version:", st.__version__)

st.title("Crossref DOI Title Checker")
st.write("Paste DOIs below (one DOI per line), then click **Check DOIs**.")

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

    return {"DOI": doi, "Title (Crossref)": title, "Journal": journal, "Year": year}

# 2) 正確是 st.text_area（不是 st.textarea）
doi_input = st.text_area(
    "DOIs",
    height=150,
    placeholder="10.1016/j.compedu.2010.01.007\n10.1016/j.compedu.2010.02.007",
)

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
                except Exception:
                    results.append({"DOI": doi, "Title (Crossref)": "ERROR", "Journal": "", "Year": ""})

        st.success(f"Checked {len(results)} DOIs")
        st.dataframe(results, use_container_width=True)
