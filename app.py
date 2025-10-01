import csv
import io
import streamlit as st
import pandas as pd

# --- Fungsi untuk load data ---
def load_news(uploaded_file):
    """Baca file berita dari file uploader"""
    try:
        reader = csv.DictReader(io.StringIO(uploaded_file.getvalue().decode('utf-8')))
        berita = []
        for row in reader:
            berita.append({
                "IdBerita": (row.get("IdBerita") or "").strip(),
                "Headline": (row.get("Headline") or "").strip(),
                "Content": (row.get("Content") or "").strip(),
            })
        return berita
    except Exception as e:
        st.error(f"Gagal membaca file berita: {e}")
        return []

def load_comments(uploaded_file):
    """Baca file komentar dari file uploader"""
    try:
        reader = csv.DictReader(io.StringIO(uploaded_file.getvalue().decode('utf-8')))
        komen = []
        for row in reader:
            komen.append({
                "IdKomentar": (row.get("IdKomentar") or "").strip(),
                "IdBerita": (row.get("IdBerita") or "").strip(),
                "Komentar": (row.get("Komentar") or "").strip(),
                "Rating": float(row.get("Rating") or 0),
            })
        return komen
    except Exception as e:
        st.error(f"Gagal membaca file komentar: {e}")
        return []

# --- Fungsi untuk memproses data ---
def process_data(news_list, comments_list):
    comments_per_news = {}

    for c in comments_list:
        idb = c['IdBerita']
        rating = c['Rating']
        if idb not in comments_per_news:
            comments_per_news[idb] = {'ratings': [], 'count': 0}
        comments_per_news[idb]['ratings'].append(rating)
        comments_per_news[idb]['count'] += 1

    result = []
    for n in news_list:
        idb = n['IdBerita']
        headline = n['Headline']
        if idb in comments_per_news:
            ratings = comments_per_news[idb]['ratings']
            jumlah = comments_per_news[idb]['count']
            rata = sum(ratings) / jumlah if jumlah > 0 else 0
        else:
            rata = 0
            jumlah = 0
        result.append({
            'ID Berita': idb,
            'Headline': headline,
            'Rata-rata Rating': round(rata, 2),
            'Jumlah Komentar': jumlah
        })

    result.sort(key=lambda item: (item['Jumlah Komentar'], item['Rata-rata Rating']), reverse=True)
    return result

# --- Fungsi utama Streamlit ---
def main():
    st.set_page_config(page_title="Analisis Berita", layout="wide")
    st.title("📊 Analisis Sentimen & Popularitas Berita")
    st.write("Unggah file berita dan komentar untuk melihat analisis rating dan jumlah komentar.")

    col1, col2 = st.columns(2)
    with col1:
        news_file = st.file_uploader("📄 Unggah file berita (CSV)", type="csv")
    with col2:
        comments_file = st.file_uploader("💬 Unggah file komentar (CSV)", type="csv")

    if news_file and comments_file:
        news_list = load_news(news_file)
        comments_list = load_comments(comments_file)

        if news_list and comments_list:
            hasil = process_data(news_list, comments_list)
            df_hasil = pd.DataFrame(hasil)

            st.subheader("📈 Hasil Analisis")
            st.dataframe(df_hasil, use_container_width=True)

            st.markdown("### 🔍 Statistik Tambahan")
            total_berita = len(news_list)
            total_komentar = len(comments_list)
            berita_tanpa_komentar = sum(1 for item in hasil if item['Jumlah Komentar'] == 0)

            st.metric("Total Berita", total_berita)
            st.metric("Total Komentar", total_komentar)
            st.metric("Berita Tanpa Komentar", berita_tanpa_komentar)

        else:
            st.warning("Pastikan kedua file memiliki format yang benar dan tidak kosong.")

if __name__ == "__main__":
    main()
