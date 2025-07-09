import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.title("温度・湿度比較ツール")
st.markdown("""
#### 複数のCSVファイルを選択して、それぞれの
1. 最高気温（temp_max）
2. 最低気温（temp_min）
3. 平均気温（temp_avg）
4. 平均湿度（hum_avg）
5. 最低湿度（hum_min）
6. 最高湿度（hum_max）
を重ねて日別グラフ表示します。
""")

uploaded_files = st.file_uploader("CSVファイルを複数選択", accept_multiple_files=True, type="csv")

if uploaded_files:
    summary_data = []

    for uploaded_file in uploaded_files:
        label = os.path.splitext(uploaded_file.name)[0]  # ファイル名をラベルに
        df = pd.read_csv(uploaded_file)

        if 'terminal_date' not in df.columns or 'temperature' not in df.columns or 'humidity' not in df.columns:
            st.warning(f"{label} は必要なカラムがありません（terminal_date, temperature, humidity）")
            continue

        df['terminal_date'] = pd.to_datetime(df['terminal_date'], errors='coerce')
        df = df.dropna(subset=['terminal_date'])
        df['date'] = df['terminal_date'].dt.date

        grouped = df.groupby('date').agg({
            'temperature': ['max', 'min', 'mean'],
            'humidity': ['max', 'min', 'mean']
        })
        grouped.columns = ['temp_max', 'temp_min', 'temp_avg', 'hum_max', 'hum_min', 'hum_avg']
        grouped['label'] = label
        summary_data.append(grouped.reset_index())

    if summary_data:
        summary_df = pd.concat(summary_data)

        def plot_metric(metric, ylabel):
            plt.figure(figsize=(10, 5))
            for label in summary_df['label'].unique():
                subset = summary_df[summary_df['label'] == label]
                plt.plot(subset['date'], subset[metric], label=label)
            plt.title(metric.replace('_', ' ').title())
            plt.xlabel("Date")
            plt.ylabel(ylabel)
            plt.legend()
            plt.grid(True)
            st.pyplot(plt)

        st.subheader("📊 グラフ表示")
        plot_metric('temp_max', 'Max Temperature (°C)')
        plot_metric('temp_min', 'Min Temperature (°C)')
        plot_metric('temp_avg', 'Avg Temperature (°C)')
        plot_metric('hum_avg', 'Avg Humidity (%)')
        plot_metric('hum_min', 'Min Humidity (%)')
        plot_metric('hum_max', 'Max Humidity (%)')
    else:
        st.warning("有効なデータがありませんでした。")