import streamlit as st
import requests
from time import sleep

# 1) set_page_config 必須放最上面（第一個 Streamlit 指令）
st.set_page_config(page_title="Crossref DOI Title Checker", layout="centered")

import streamlit as st
import streamlit_authenticator as stauth
import inspect

def secrets_to_dict(x):
    if hasattr(x, "to_dict"):
        return secrets_to_dict(x.to_dict())
    if isinstance(x, dict):
        return {k: secrets_to_dict(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [secrets_to_dict(v) for v in x]
    return x

# ===== 1) 先把 secrets 轉成一般 dict =====
auth_config = secrets_to_dict(st.secrets["auth"])

# ===== 2) 先建立 authenticator（這行一定要在 safe_login 前面）=====
authenticator = stauth.Authenticate(
    auth_config["credentials"],
    auth_config["cookie_name"],
    auth_config["cookie_key"],
    auth_config["cookie_expiry_days"],
)

# ===== 3) 再登入（只呼叫一次，避免 duplicate form）=====
def safe_login(authenticator):
    fn = authenticator.login

    # 只允許「成功命中其中一種呼叫方式」就立刻回傳
    # 注意：要同時 catch TypeError / ValueError，因為你前面也遇過 ValueError(location 限制)
    for call in [
        lambda: fn("登入系統", "main"),          # 常見： (form_name, location)
        lambda: fn("main", "登入系統"),          # 你雲端看起來像： (location, form_name)
        lambda: fn("登入系統"),                  # 少數：只吃 form_name
        lambda: fn(),                            # 少數：不吃參數
        lambda: fn(location="main"),             # 有些版才吃 keyword
        lambda: fn("登入系統", location="main"), # 有些新版才吃 keyword
    ]:
        try:
            return call()
        except (TypeError, ValueError):
            continue

    # 如果所有模式都不支援，直接拋錯（讓你看到真錯誤）
    raise RuntimeError("streamlit-authenticator.login() 介面不相容：所有呼叫模式都失敗")


login_ret = safe_login(authenticator)

# ===== 4) 讀取結果（以 session_state 為主）=====
authentication_status = st.session_state.get("authentication_status", None)
name = st.session_state.get("name", "")
username = st.session_state.get("username", "")

if authentication_status is True:
    with st.sidebar:
        try:
            authenticator.logout("登出", "sidebar")
        except TypeError:
            authenticator.logout("登出")
        st.caption(f"登入者：{name} ({username})")
elif authentication_status is False:
    st.error("帳號或密碼錯誤")
    st.stop()
else:
    st.warning("請先登入")
    st.


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

