import os
import sqlite3
from pathlib import Path
from collections import deque

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="DS3 Death Counter",
                   page_icon="💀", layout="wide")

DB_PATH = os.getenv("DB_PATH", "db.sqlite")
DEATHS_DIR = Path(os.getenv("SCREENSHOTS_DIR", "screenshots")) / "deaths"
LOG_FILE = Path(os.getenv("LOG_FILE", "logs.log"))
COLUMNS = 4
GOLD = "#c8a24a"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"]


@st.cache_data(ttl=5)
def load_deaths() -> pd.DataFrame:
    try:
        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=5) as conn:
            df = pd.read_sql(
                "SELECT id, stream_title, timestamp FROM deaths", conn)
    except sqlite3.OperationalError:
        df = pd.DataFrame(columns=["id", "stream_title", "timestamp"])
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], utc=True).dt.tz_convert("America/Sao_Paulo")
    df["stream_title"] = df["stream_title"].fillna("Unknown")
    return df


def get_images():
    return sorted(
        DEATHS_DIR.glob("*.png"),
        key=lambda p: int(p.stem) if p.stem.isdigit() else 0,
        reverse=True,
    )


def fmt_td(td) -> str:
    if pd.isna(td):
        return "-"
    s = int(td.total_seconds())
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m:02d}m" if h else f"{m}m {s:02d}s"


def style(chart, height=260):
    return chart.properties(height=height).configure_view(strokeWidth=0)


# ---------- Header ----------
head_l, head_r = st.columns([4, 1], vertical_alignment="bottom")
with head_l:
    st.title("💀 Flamingo_Lindo's")
    st.caption("Dark Souls 3 Death Counter")


# ---------- Dashboard ----------
@st.fragment(run_every="5s")
def dashboard():
    df = load_deaths()
    images = get_images()

    if df.empty:
        st.info("No deaths recorded yet. Lucky you.")
        return

    df = df.sort_values("timestamp")
    now = pd.Timestamp.now(tz=df["timestamp"].dt.tz)
    today = df[df["timestamp"].dt.date == now.date()]
    yesterday = df[df["timestamp"].dt.date ==
                   (now - pd.Timedelta(days=1)).date()]
    gaps = df["timestamp"].diff().dropna()

    # --- KPI cards ---
    k1, k2, k3, k4 = st.columns(4)
    with k1, st.container(border=True):
        st.metric("Total deaths", len(df))
    with k2, st.container(border=True):
        st.metric("Today", len(today), delta=len(today) -
                  len(yesterday), delta_color="inverse")
    with k3, st.container(border=True):
        st.metric("Avg time between deaths", fmt_td(gaps.mean()))
    with k4, st.container(border=True):
        st.metric("Longest survival", fmt_td(gaps.max()))

    tab_overview, tab_patterns, tab_streams, tab_gallery = st.tabs(
        ["📈 Overview", "🕒 Patterns", "🎮 Streams", "🖼️ Hall of shame"]
    )

    # --- Overview ---
    with tab_overview:
        per_day = df.set_index("timestamp").resample(
            "D").size().rename("deaths").reset_index()
        per_day["total"] = per_day["deaths"].cumsum()

        c1, c2 = st.columns(2)
        with c1, st.container(border=True):
            st.markdown("**Deaths per day**")
            bars = alt.Chart(per_day).mark_bar(color=GOLD, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X("timestamp:T", title=None),
                y=alt.Y("deaths:Q", title=None),
                tooltip=[alt.Tooltip("timestamp:T", title="Day"), "deaths"],
            )
            st.altair_chart(style(bars), width="stretch")
        with c2, st.container(border=True):
            st.markdown("**Cumulative deaths**")
            area = alt.Chart(per_day).mark_area(
                color=GOLD, opacity=0.35, line={"color": GOLD}
            ).encode(
                x=alt.X("timestamp:T", title=None),
                y=alt.Y("total:Q", title=None),
                tooltip=[alt.Tooltip("timestamp:T", title="Day"), "total"],
            )
            st.altair_chart(style(area), width="stretch")

    # --- Patterns ---
    with tab_patterns:
        heat = (
            df.assign(weekday=df["timestamp"].dt.day_name(),
                      hour=df["timestamp"].dt.hour)
            .groupby(["weekday", "hour"]).size().reset_index(name="deaths")
        )
        with st.container(border=True):
            st.markdown("**When do you die?** (weekday × hour)")
            heatmap = alt.Chart(heat).mark_rect(cornerRadius=3).encode(
                x=alt.X("hour:O", title="Hour of day"),
                y=alt.Y("weekday:N", sort=WEEKDAYS, title=None),
                color=alt.Color("deaths:Q", scale=alt.Scale(
                    scheme="oranges"), legend=None),
                tooltip=["weekday", "hour", "deaths"],
            )
            st.altair_chart(style(heatmap, 280), width="stretch")

        c1, c2 = st.columns(2)
        with c1, st.container(border=True):
            st.markdown("**By hour**")
            by_hour = df.groupby(df["timestamp"].dt.hour).size().reindex(
                range(24), fill_value=0)
            by_hour = by_hour.rename_axis("hour").reset_index(name="deaths")
            st.altair_chart(style(
                alt.Chart(by_hour).mark_bar(color=GOLD).encode(
                    x=alt.X("hour:O", title=None), y=alt.Y("deaths:Q", title=None),
                    tooltip=["hour", "deaths"])
            ), width="stretch")
        with c2, st.container(border=True):
            st.markdown("**By weekday**")
            by_day = df.groupby(df["timestamp"].dt.day_name()).size().reindex(
                WEEKDAYS, fill_value=0)
            by_day = by_day.rename_axis("weekday").reset_index(name="deaths")
            st.altair_chart(style(
                alt.Chart(by_day).mark_bar(color=GOLD).encode(
                    x=alt.X("weekday:N", sort=WEEKDAYS, title=None,
                            axis=alt.Axis(labelAngle=-30)),
                    y=alt.Y("deaths:Q", title=None), tooltip=["weekday", "deaths"])
            ), width="stretch")

    # --- Streams ---
    with tab_streams:
        g = df.groupby("stream_title")["timestamp"].agg(
            ["count", "min", "max"])
        g["hours"] = ((g["max"] - g["min"]).dt.total_seconds() /
                      3600).clip(lower=0.1)
        g["per_hour"] = (g["count"] / g["hours"]).round(1)
        g = g.reset_index().rename(columns={"count": "deaths"})

        c1, c2 = st.columns(2)
        with c1, st.container(border=True):
            st.markdown("**Deaths per stream** (top 10)")
            top = g.sort_values("deaths", ascending=False).head(10)
            st.altair_chart(style(
                alt.Chart(top).mark_bar(color=GOLD, cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
                    y=alt.Y("stream_title:N", sort="-x", title=None,
                            axis=alt.Axis(labelLimit=220)),
                    x=alt.X("deaths:Q", title=None),
                    tooltip=["stream_title", "deaths"]),
                height=300,
            ), width="stretch")
        with c2, st.container(border=True):
            st.markdown("**Death rate per stream**")
            st.dataframe(
                g.sort_values("per_hour", ascending=False)[
                    ["stream_title", "deaths", "per_hour"]],
                hide_index=True,
                height=300,
                column_config={
                    "stream_title": st.column_config.TextColumn("Stream"),
                    "deaths": st.column_config.NumberColumn("Deaths"),
                    "per_hour": st.column_config.ProgressColumn(
                        "Deaths / hour", min_value=0, max_value=float(g["per_hour"].max()), format="%.1f"),
                },
                width="stretch",
            )

    # --- Gallery ---
    with tab_gallery:
        if not images:
            st.info("No screenshots yet.")
        with st.container(height=650, border=False):
            st.write("")  # headroom so the first row's button isn't clipped
            for start in range(0, len(images), COLUMNS):
                cols = st.columns(COLUMNS)
                for col, img in zip(cols, images[start:start + COLUMNS]):
                    with col, st.container(border=True):
                        st.markdown(f"**Death #{img.stem}**")
                        st.image(str(img), width="stretch")


dashboard()

# ---------- Logs ----------
with st.expander("Logs", icon=":material/terminal:"):
    log_file = LOG_FILE

    @st.fragment(run_every="2s")
    def log_view():
        if log_file.exists():
            with log_file.open(errors="replace") as f:
                lines = deque(f, maxlen=200)
            st.code("".join(reversed(lines)), language="log", height=300)
        else:
            st.info("No log file yet.")

    log_view()
