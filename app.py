import streamlit as st
import pandas as pd
import qrcode
import os
from datetime import datetime
import geocoder

# CONFIG
SHOP_NAME = "Makkah Autos"
PHONE = "0346-8395057"

# FILES
products_file = "products.csv"
scans_file = "scans.csv"

if not os.path.exists(scans_file):
    pd.DataFrame(columns=["code","name","phone","location","time","count"]).to_csv(scans_file, index=False)

products = pd.read_csv(products_file)
scans = pd.read_csv(scans_file)

st.set_page_config(page_title="Makkah Autos Verification", layout="centered")

# STYLE
st.markdown("""
<style>
.big-title {text-align:center; font-size:35px; font-weight:bold;}
.success-box {background:#0f5132; color:white; padding:20px; border-radius:10px;}
.error-box {background:#842029; color:white; padding:20px; border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<div class='big-title'>{SHOP_NAME}</div>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("Menu", ["Generate Stickers","Verify Product","Dashboard"])

# ------------------- GENERATE STICKERS -------------------
if menu == "Generate Stickers":
    st.subheader("QR Sticker Generator")

    base_url = "http://localhost:8501/?code="

    for i, row in products.iterrows():
        code = row["unique_code"]

        qr = qrcode.make(base_url + code)
        path = f"stickers/{code}.png"
        qr.save(path)

        st.image(path, caption=f"{SHOP_NAME} | Code: {code}")

# ------------------- VERIFY -------------------
elif menu == "Verify Product":
    st.subheader("Product Verification")

    code = st.query_params.get("code","")

    name = st.text_input("Customer Name")
    phone = st.text_input("WhatsApp Number")
    input_code = st.text_input("Verification Code", value=code)

    if st.button("Verify"):
        if input_code in products["unique_code"].values:

            g = geocoder.ip('me')
            location = g.city

            # Count check
            existing = scans[scans["code"] == input_code]
            count = len(existing) + 1

            new_scan = pd.DataFrame([{
                "code": input_code,
                "name": name,
                "phone": phone,
                "location": location,
                "time": datetime.now(),
                "count": count
            }])

            new_scan.to_csv(scans_file, mode='a', header=False, index=False)

            st.markdown(f"""
            <div class="success-box">
            ✅ Genuine Product <br><
            br>
            Code: {input_code} <br>
            Verified Times: {count}
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="error-box">
            ❌ Fake Product
            </div>
            """, unsafe_allow_html=True)

# ------------------- DASHBOARD -------------------
elif menu == "Dashboard":
    st.subheader("Scan Data")

    scans = pd.read_csv(scans_file)

    st.dataframe(scans)
    st.bar_chart(scans["code"].value_counts())
    