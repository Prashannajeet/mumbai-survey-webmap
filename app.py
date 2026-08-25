from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
GEOJSON_PATH = ROOT / "output" / "mumbai_survey_points.geojson"
PROFILE_PATH = ROOT / "output" / "data_quality_profile.csv"
SOURCE_CRS = "WGS 84 / UTM Zone 43N (EPSG:32643)"

BLUE = "#176B87"
ORANGE = "#D98E04"
INK = "#17212B"
CODE_COLOURS = {
    "FT": BLUE,
    "LV": ORANGE,
    "CH": "#7C8C3C",
    "ROAD LV": "#B44C72",
    "CHTOP": "#68478D",
    "Other / rare": "#A7AFB7",
}


st.set_page_config(
    page_title="Mumbai Survey Web Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1500px;}
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {display:none;}
    [data-testid="stMetric"] {background:#f7f9fb; border:1px solid #e4e9ee; padding:14px 16px; border-radius:12px;}
    [data-testid="stMetricLabel"] {color:#52606d;}
    [data-testid="stPlotlyChart"] {border:0 !important; box-shadow:none !important;}
    h1, h2, h3 {color:#17212b;}
    .source-note {font-size:.86rem; color:#64717d;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_points(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as handle:
        geojson = json.load(handle)

    rows = []
    for feature in geojson.get("features", []):
        coordinates = feature.get("geometry", {}).get("coordinates", [None, None])
        properties = feature.get("properties", {}).copy()
        properties["longitude"] = coordinates[0]
        properties["latitude"] = coordinates[1]
        rows.append(properties)

    frame = pd.DataFrame(rows)
    required = {"ID", "Easting", "Northing", "Elevation", "Code", "longitude", "latitude"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")

    for column in ["Easting", "Northing", "Elevation", "longitude", "latitude"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["Code"] = frame["Code"].fillna("(missing)").astype(str).str.strip().str.upper()
    frame["Code_group"] = frame.get("Code_group", "Other / rare").fillna("Other / rare")
    return frame.dropna(subset=["longitude", "latitude", "Elevation"])


@st.cache_data(show_spinner=False)
def load_profile(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def map_figure(data: pd.DataFrame, colour_by: str, map_style: str) -> go.Figure:
    hover = {
        "ID": True,
        "Code": True,
        "Elevation": ":.3f",
        "Easting": ":.3f",
        "Northing": ":.3f",
        "latitude": False,
        "longitude": False,
    }
    if colour_by == "Elevation":
        fig = px.scatter_map(
            data,
            lat="latitude",
            lon="longitude",
            color="Elevation",
            color_continuous_scale="Plasma",
            hover_name="ID",
            hover_data=hover,
            zoom=15,
            height=650,
        )
        fig.update_coloraxes(colorbar_title="Elevation")
    else:
        fig = px.scatter_map(
            data,
            lat="latitude",
            lon="longitude",
            color="Code_group",
            color_discrete_map=CODE_COLOURS,
            hover_name="ID",
            hover_data=hover,
            zoom=15,
            height=650,
        )
        fig.update_layout(legend_title_text="Feature code")

    fig.update_traces(marker={"size": 9, "opacity": 0.88})
    fig.update_layout(
        map_style=map_style,
        map_bounds={"west": data.longitude.min(), "east": data.longitude.max(),
                    "south": data.latitude.min(), "north": data.latitude.max()},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="white",
        font={"color": INK},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.01, "x": 0},
    )
    return fig


try:
    points = load_points(str(GEOJSON_PATH))
    profile = load_profile(str(PROFILE_PATH))
except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
    st.error(f"Dashboard data could not be loaded: {exc}")
    st.info("Run `Rscript mumbai_survey_analysis.R` to regenerate the GIS outputs.")
    st.stop()

st.title("Mumbai Survey Web Map")
st.markdown(
    f'<div class="source-note">Survey dated 23 Aug 2026 · {SOURCE_CRS} · '
    f'{len(points):,} mapped records</div>',
    unsafe_allow_html=True,
)

st.markdown("#### Filters")
filter_code, filter_elevation, filter_colour, filter_basemap = st.columns([2.2, 2.2, 1.25, 1.15])
with filter_code:
    code_options = sorted(points["Code"].unique().tolist())
    selected_codes = st.multiselect(
        "Feature codes",
        code_options,
        default=[],
        placeholder="All feature codes",
        help="Leave empty to show every feature code.",
    )
with filter_elevation:
    elevation_min = float(points["Elevation"].min())
    elevation_max = float(points["Elevation"].max())
    selected_elevation = st.slider(
        "Elevation range",
        min_value=elevation_min,
        max_value=elevation_max,
        value=(elevation_min, elevation_max),
        step=0.1,
        format="%.1f",
    )
with filter_colour:
    colour_by = st.selectbox("Map colouring", ["Elevation", "Feature code"])
with filter_basemap:
    basemap_label = st.selectbox("Basemap", ["Street", "Light"])
    map_style = "open-street-map" if basemap_label == "Street" else "carto-positron"

filtered = points.loc[
    (points["Code"].isin(selected_codes) if selected_codes else points.index == points.index)
    & points["Elevation"].between(selected_elevation[0], selected_elevation[1])
].copy()

if filtered.empty:
    st.warning("No survey points match the selected filters.")
    st.stop()

metric_cols = st.columns(5)
metric_cols[0].metric("Survey points", f"{len(filtered):,}")
metric_cols[1].metric("Feature codes", f"{filtered['Code'].nunique():,}")
metric_cols[2].metric("Min elevation", f"{filtered['Elevation'].min():.2f}")
metric_cols[3].metric("Median elevation", f"{filtered['Elevation'].median():.2f}")
metric_cols[4].metric("Max elevation", f"{filtered['Elevation'].max():.2f}")

st.subheader("Full survey extent")
st.plotly_chart(map_figure(filtered, colour_by, map_style))
st.caption("Coordinates transformed from confirmed EPSG:32643 to WGS 84 for web display.")

st.subheader("Survey diagnostics")
left, right = st.columns([1.25, 1])
with left:
    histogram = px.histogram(
        filtered,
        x="Elevation",
        nbins=30,
        color_discrete_sequence=[BLUE],
        labels={"Elevation": "Elevation (source units)", "count": "Survey points"},
    )
    histogram.update_layout(
        title="Elevation distribution",
        showlegend=False,
        margin={"l": 0, "r": 10, "t": 55, "b": 0},
        yaxis_title="Survey points",
    )
    st.plotly_chart(histogram)
with right:
    counts = filtered["Code"].value_counts().head(12).sort_values().rename_axis("Code").reset_index(name="Records")
    bars = px.bar(
        counts,
        x="Records",
        y="Code",
        orientation="h",
        color_discrete_sequence=[ORANGE],
        text="Records",
    )
    bars.update_layout(title="Most frequent feature codes", margin={"l": 0, "r": 10, "t": 55, "b": 0})
    bars.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(bars)

qa = profile.set_index("metric")["value"]
st.caption(
    f"Complete coordinate/elevation rows: {int(qa.get('complete coordinate/elevation rows', 0)):,} · "
    f"Exact duplicate rows: {int(qa.get('exact duplicate rows', 0)):,} · "
    f"Repeated coordinate pairs after the first: {int(qa.get('duplicate coordinate pairs', 0)):,}"
)

st.subheader("Survey records")
detail_columns = ["ID", "Code", "Elevation", "Easting", "Northing", "latitude", "longitude"]
detail = filtered[detail_columns].sort_values(["Code", "ID"], na_position="last")
st.dataframe(
    detail,
    width="stretch",
    hide_index=True,
    column_config={
        "Elevation": st.column_config.NumberColumn(format="%.3f"),
        "Easting": st.column_config.NumberColumn(format="%.3f"),
        "Northing": st.column_config.NumberColumn(format="%.3f"),
        "latitude": st.column_config.NumberColumn(format="%.6f"),
        "longitude": st.column_config.NumberColumn(format="%.6f"),
    },
)
st.download_button(
    "Download filtered records",
    data=detail.to_csv(index=False).encode("utf-8"),
    file_name="mumbai_survey_filtered.csv",
    mime="text/csv",
)

st.divider()
st.caption("Source: 23-08-2026 TOTAL.csv · Analysis and GIS preparation: R · Dashboard: Streamlit")
