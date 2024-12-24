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
    elif isinstance(b, float):
        return a ** b
    else:
        def rekursif(a, b):
            if b == 0:
                return 1
            elif b % 2 == 0:
                half = rekursif(a, b // 2)
                return half * half
            else:
                return a * rekursif(a, b - 1)

        return rekursif(a, b)

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
            df['Hasil (Iterative)'] = results_iterative
            df['T(b) Iterative'] = times_iterative
            df['Hasil (Recursive)'] = results_recursive
            df['T(b-1) + O(1) Recursive'] = times_recursive

            # Tampilkan hasil dan waktu eksekusi
            st.write("### Data dengan Hasil dan Waktu Eksekusi:")
            st.dataframe(df)

            # Grafik
            st.write("### Grafik Running Time")
            sample_data = df.iloc[:5]
            x_axis = sample_data.index.tolist()

            option_combined = {
                "xAxis": {"type": "category", "data": x_axis},
                "yAxis": {"type": "value"},
                "legend": {"data": ["Iterative", "Recursive"]},
                "series": [
                    {"data": sample_data['T(b) Iterative'].tolist(), "type": "line", "name": "Iterative"},
                    {"data": sample_data['T(b-1) + O(1) Recursive'].tolist(), "type": "line", "name": "Recursive"},
                ],
            }

            st_echarts(option_combined, height="400px")

           # Rata-rata waktu eksekusi
            avg_time_iterative = sum(times_iterative) / len(times_iterative)
            avg_time_recursive = sum(times_recursive) / len(times_recursive)

            # Tampilkan rata-rata waktu eksekusi
            st.write("### Rata-rata Waktu Eksekusi:")
            st.write(f"- Metode **Iteratif**: {avg_time_iterative:.2f} µs")
            st.write(f"- Metode **Rekursif**: {avg_time_recursive:.2f} µs")

            # Kesimpulan
            st.write("### Kesimpulan:")
            if avg_time_iterative < avg_time_recursive:
                st.write(f"Metode **Iteratif** lebih cepat dengan waktu rata-rata {avg_time_iterative:.2f} µs.")
            else:
                st.write(f"Metode **Rekursif** lebih cepat dengan waktu rata-rata {avg_time_recursive:.2f} µs.")


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
