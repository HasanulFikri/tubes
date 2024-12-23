import streamlit as st
import pandas as pd
from fractions import Fraction
from streamlit_echarts import st_echarts
import time
import math

# Fungsi iteratif

def revised_power(a, b):
    try:
        if b == 0:
            if a == 0:
                raise ValueError("0^0 tidak terdefinisi.")
            return 1

        if a == 0 and b < 0:
            raise ZeroDivisionError("Tidak dapat menghitung 1 / 0.")

        # Untuk eksponen negatif
        if b < 0:
            b = -b
            inverse = True
        else:
            inverse = False

        # Untuk eksponen pecahan
        if isinstance(b, float) and (b % 1 != 0):
            fraction = Fraction(b).limit_denominator()
            p, n = fraction.numerator, fraction.denominator
            result_p = 1
            while p > 0:
                if p % 2 == 1:
                    result_p *= a
                a *= a
                p //= 2

            root = result_p
            if n % 2 == 0 and root < 0:
                raise ValueError("Akar genap dari bilangan negatif tidak valid.")

            result = math.copysign(math.pow(abs(root), 1 / n), root)
        else:
            result = 1
            while b > 0:
                if b % 2 == 1:
                    result *= a
                a *= a
                b //= 2

            if inverse:
                result = 1 / result

        return result
    except Exception as e:
        return str(e)

# Fungsi rekursif
def eksponen(a, b):
    if b == 0:
        return 1
    elif b < 0:
        return 1 / eksponen(a, -b)
    elif isinstance(b, float) and b != int(b):
        return a ** b
    elif b % 2 == 0:
        half = eksponen(a, b // 2)
        return half * half
    else:
        return a * eksponen(a, b - 1)

# Streamlit interface
st.title("Aplikasi Eksponen: Iteratif vs Rekursif")

# File uploader
uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Membaca file Excel
        df = pd.read_excel(uploaded_file)
        st.write("Data Awal:")
        st.dataframe(df)

        if 'a' in df.columns and 'b' in df.columns:
            results_iterative = []
            results_recursive = []
            times_iterative = []
            times_recursive = []

            for _, row in df.iterrows():
                a, b = row['a'], row['b']

                # Iteratif
                start_time = time.perf_counter()
                result_iter = revised_power(a, b)
                end_time = time.perf_counter()
                times_iterative.append((end_time - start_time) * 1_000_000)
                results_iterative.append(result_iter)

                # Rekursif
                start_time = time.perf_counter()
                result_rec = eksponen(a, b)
                end_time = time.perf_counter()
                times_recursive.append((end_time - start_time) * 1_000_000)
                results_recursive.append(result_rec)

            # Tambahkan hasil dan waktu eksekusi ke dataframe
            df['Result (Iterative)'] = results_iterative
            df['T(n) Iterative (µs)'] = times_iterative
            df['Result (Recursive)'] = results_recursive
            df['T(n) Recursive (µs)'] = times_recursive

            # Tampilkan hasil dan waktu eksekusi
            st.write("### Data dengan Hasil dan Waktu Eksekusi:")
            st.dataframe(df)

            # Grafik
            st.write("### Grafik Running Time")
            x_axis = df.index.tolist()

            option_iterative = {
                "xAxis": {"type": "category", "data": x_axis},
                "yAxis": {"type": "value"},
                "series": [{"data": times_iterative, "type": "line", "name": "Iterative"}],
            }

            option_recursive = {
                "xAxis": {"type": "category", "data": x_axis},
                "yAxis": {"type": "value"},
                "series": [{"data": times_recursive, "type": "line", "name": "Recursive"}],
            }

            col1, col2 = st.columns(2)
            with col1:
                st.write("#### Iterative")
                st_echarts(option_iterative, height="400px")
            with col2:
                st.write("#### Recursive")
                st_echarts(option_recursive, height="400px")

            # Unduh hasil sebagai Excel
            @st.cache_data
            def convert_df_to_excel(df):
                return df.to_excel(index=False, engine='openpyxl')

            st.download_button(
                label="Unduh Hasil",
                data=convert_df_to_excel(df),
                file_name="hasil_perhitungan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Pastikan file memiliki kolom 'a' dan 'b'.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
