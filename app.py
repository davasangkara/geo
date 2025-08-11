import os
from datetime import datetime
import pandas as pd
import streamlit as st

# Komponen geolokasi (pakai HTML5 Geolocation di browser)
# pip install streamlit-geolocation
from streamlit_geolocation import st_geolocation

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "changeme")  # ganti via ENV atau secrets

st.set_page_config(page_title="Geo Demo (Streamlit)", page_icon="📍", layout="centered")
st.title("📍 Consent-based Geolocation (Streamlit, no DB)")

@st.cache_resource
def get_store():
    # Penyimpanan global sederhana di memori proses (hilang jika app restart)
    return []

HITS = get_store()

tab_share, tab_admin = st.tabs(["Share Location", "Admin"])

with tab_share:
    st.write("Klik tombol di bawah. Browser akan **minta izin** dulu; kalau ditolak, tidak ada data dikirim.")
    loc = st_geolocation()  # tampilkan tombol dan ambil lokasi saat user setuju
    if loc:
        lat = loc.get("latitude")
        lon = loc.get("longitude")
        acc = loc.get("accuracy")
        if lat is not None and lon is not None:
            hit = {
                "id": len(HITS) + 1,
                "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "lat": float(lat),
                "lon": float(lon),
                "accuracy": float(acc) if acc is not None else None,
            }
            HITS.append(hit)
            msg = f"Lokasi diterima: lat={lat:.6f}, lon={lon:.6f}"
            if acc is not None: msg += f", ±{acc:.0f}m"
            st.success(msg)
            st.link_button("Buka di Google Maps", f"https://www.google.com/maps?q={lat},{lon}")
            st.map(pd.DataFrame([{"lat": lat, "lon": lon}]))
        else:
            st.warning("Tidak mendapat koordinat (browser menolak atau sensor tidak aktif).")

    st.caption("Tips akurasi: pakai HP (GPS ON) & aktifkan precise location. Di Streamlit Cloud sudah HTTPS, jadi geolocation jalan.")

with tab_admin:
    st.write("Masukkan token admin untuk melihat log.")
    token = st.text_input("Admin token", type="password", placeholder="isi token di sini")
    if token:
        if token == ADMIN_TOKEN:
            st.success("Token valid ✔️")
            if HITS:
                df = pd.DataFrame(HITS)
                cols = ["id", "ts", "lat", "lon", "accuracy"]
                df = df.reindex(columns=cols)
                st.dataframe(df, use_container_width=True)
                st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"),
                                   "geo_log.csv", "text/csv")
                # peta titik terakhir
                last = HITS[-1]
                st.map(pd.DataFrame([{"lat": last["lat"], "lon": last["lon"]}]))
            else:
                st.info("Belum ada data lokasi.")
        else:
            st.error("Token salah.")
    st.caption("Set token via ENV ADMIN_TOKEN atau biarkan default `changeme` (hanya untuk testing).")
