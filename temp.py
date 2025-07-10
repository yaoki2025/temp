import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.title("温度・湿度比較ツール（インタラクティブ表示）")
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
        label = os.path.splitext(uploaded_file.name)[0]
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

        def plot_metric_plotly(df, metric, ylabel):
            fig = px.line(
                df,
                x="date",
                y=metric,
                color="label",
                markers=True,
                labels={
                    "date": "日付",
                    metric: ylabel,
                    "label": "ファイル"
                },
                title=f"{ylabel} の日別推移"
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 グラフ表示（インタラクティブ）")
        plot_metric_plotly(summary_df, 'temp_max', '最高気温 (°C)')
        plot_metric_plotly(summary_df, 'temp_min', '最低気温 (°C)')
        plot_metric_plotly(summary_df, 'temp_avg', '平均気温 (°C)')
        plot_metric_plotly(summary_df, 'hum_avg', '平均湿度 (%)')
        plot_metric_plotly(summary_df, 'hum_min', '最低湿度 (%)')
        plot_metric_plotly(summary_df, 'hum_max', '最高湿度 (%)')

        # 👇 追加：すべてのファイルの「年ごとの平均気温（通日比較）」を重ねて表示
        st.subheader("📅 年ごとの平均気温（temp_avg）の比較（通日）")

        year_data = []

        for grouped_df in summary_data:
            label = grouped_df['label'].iloc[0]
            temp_df = grouped_df.copy()
            temp_df['date'] = pd.to_datetime(temp_df['date'])
            temp_df['year'] = temp_df['date'].dt.year
            temp_df['day_of_year'] = temp_df['date'].dt.dayofyear

            for year, year_group in temp_df.groupby('year'):
                g = year_group.copy()
                g['year_label'] = f"{label}_{year}"
                year_data.append(g)

        if year_data:
            year_df = pd.concat(year_data)

            fig = px.line(
                year_df,
                x="day_of_year",
                y="temp_avg",
                color="year_label",
                labels={
                    "day_of_year": "年間通日（Day of Year）",
                    "temp_avg": "平均気温 (°C)",
                    "year_label": "ファイル_年"
                },
                title="年ごとの平均気温（通日比較）"
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("有効なデータがありませんでした。")