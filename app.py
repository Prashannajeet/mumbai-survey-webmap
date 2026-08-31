from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pyproj import Transformer


ROOT = Path(__file__).resolve().parent
GEOJSON_PATH = ROOT / "output" / "mumbai_survey_points.geojson"
SOURCE_CRS = "WGS 84 / UTM Zone 43N (EPSG:32643)"
WEB_CRS = "WGS 84 (EPSG:4326)"
UTM_TO_WGS84 = Transformer.from_crs(32643, 4326, always_xy=True)

BLUE = "#176B87"
ORANGE = "#D98E04"
INK = "#17212B"
NAVY = "#0B2239"
TEAL = "#1F7A8C"
CANVAS = "#EEF3F7"
CODE_COLOURS = {
    "FT": BLUE,
    "LV": ORANGE,
    "CH": "#7C8C3C",
    "ROAD LV": "#B44C72",
    "CHTOP": "#68478D",
    "Other / rare": "#A7AFB7",
}

ARCGIS_TILES = {
    "ArcGIS Imagery": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "ArcGIS Topographic": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    "ArcGIS Streets": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
}

INITIAL_MAP_ZOOM = 13.2

MAP_CONFIG = {
    "scrollZoom": True,
    "displayModeBar": True,
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["select2d", "lasso2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "mumbai_survey_webmap",
        "scale": 2,
    },
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
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {height:100vh; overflow:hidden;}
    [data-testid="stAppViewContainer"] {background:#eef3f7;}
    .block-container {position:fixed; inset:0; width:100%; height:100vh; padding:0.65rem 0.85rem 0.45rem; max-width:1600px; overflow:hidden;}
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {display:none;}
    [data-testid="stHeader"] {height:0; min-height:0;}
    [data-testid="stToolbar"] {top:0.2rem; right:0.4rem;}
    [data-testid="stMetric"] {background:#fff; border:1px solid #dce5eb; border-left:3px solid #1f7a8c; padding:8px 12px; border-radius:10px; box-shadow:0 2px 8px rgba(11,34,57,.06);}
    [data-testid="stMetricLabel"] {color:#526b7a; font-size:.76rem; font-weight:600; letter-spacing:.02em;}
    [data-testid="stMetricValue"] {color:#0b2239; font-weight:650;}
    [data-testid="stPlotlyChart"] {border:0 !important; box-shadow:none !important;}
    h1, h2, h3, h4 {color:#17212b; margin:0 !important;}
    h1 {font-size:1.75rem !important; line-height:1.1 !important;}
    h3 {font-size:1.05rem !important; line-height:1.35 !important; min-height:1.45rem; padding:0.1rem 0 0.25rem !important;}
    h4 {font-size:0.95rem !important; padding:0 !important;}
    .source-note {font-size:.76rem; color:#64717d; margin-bottom:0.15rem;}
    .dashboard-hero {display:flex; align-items:center; justify-content:space-between; gap:1rem; background:#0b2239; color:#fff; padding:.65rem .85rem; border-radius:12px; box-shadow:0 5px 16px rgba(11,34,57,.16);}
    .hero-spacer {height:.55rem;}
    .dashboard-title {font-size:1.35rem; line-height:1.1; font-weight:700; letter-spacing:-.02em;}
    .dashboard-meta {font-size:.73rem; color:#b9c8d3; margin-top:.18rem;}
    .status-pill {white-space:nowrap; color:#d9f1f0; background:#164b5a; border:1px solid #2b7e88; border-radius:999px; padding:.28rem .62rem; font-size:.7rem; font-weight:650;}
    [data-testid="stVerticalBlock"] {gap:0.35rem;}
    [data-testid="stHorizontalBlock"] {gap:0.65rem;}
    .stDownloadButton button {height:2.35rem; width:100%;}
    .st-key-survey_navigation_map .modebar {
        top:8px !important; right:8px !important; left:auto !important;
        display:flex !important; flex-direction:column !important;
        background:rgba(255,255,255,.96) !important;
        border:1px solid #cbd9e1; border-radius:9px; padding:3px !important;
        box-shadow:0 1px 4px rgba(23,33,43,.12);
    }
    .st-key-survey_navigation_map .modebar-group {
        display:flex !important; flex-direction:column !important;
        padding:0 !important;
    }
    .st-key-survey_navigation_map .modebar-btn {padding:4px !important;}
    .st-key-survey_navigation_map .modebar-btn path {fill:#164b5a !important;}
    .st-key-survey_navigation_map .modebar-btn:hover {background:#dff0f2 !important; border-radius:5px;}
    div[data-baseweb="select"] > div, [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background:#fff; border-color:#d8e3e9; border-radius:9px;
    }
    [data-testid="stSlider"] [role="slider"] {background:#1f7a8c !important; border-color:#fff !important;}
    [data-testid="stSlider"] div[data-testid="stTickBarMin"], [data-testid="stSlider"] div[data-testid="stTickBarMax"] {color:#526b7a;}
    .stDownloadButton button {background:#0b2239; color:#fff; border:1px solid #0b2239; border-radius:9px; font-weight:650;}
    .stDownloadButton button:hover {background:#164b5a; color:#fff; border-color:#164b5a;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_points(path: str, file_revision: int) -> pd.DataFrame:
    # file_revision participates in Streamlit's cache key so regenerated GIS
    # outputs are loaded immediately even though their path stays unchanged.
    del file_revision
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
def load_uploaded_csv(raw: bytes) -> pd.DataFrame:
    frame = pd.read_csv(BytesIO(raw))
    normalized = {str(column).strip().lower(): column for column in frame.columns}
    required_names = ["id", "northing", "easting", "elevation", "code"]
    missing = [name for name in required_names if name not in normalized]
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

    frame = frame.rename(columns={normalized[name]: name.title() for name in required_names})
    frame["ID"] = frame["Id"].astype("string").fillna("").str.strip()
    frame = frame.drop(columns=["Id"])
    for column in ["Northing", "Easting", "Elevation"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["Code"] = frame["Code"].astype("string").fillna("(missing)").str.strip().str.upper()
    frame = frame.dropna(subset=["Northing", "Easting", "Elevation"])
    if frame.empty:
        raise ValueError("CSV contains no valid coordinate and elevation rows.")
    if not frame["Easting"].between(100000, 900000).all() or not frame["Northing"].between(0, 10000000).all():
        raise ValueError("Coordinates are outside valid UTM ranges for EPSG:32643.")

    longitude, latitude = UTM_TO_WGS84.transform(frame["Easting"].to_numpy(), frame["Northing"].to_numpy())
    frame["longitude"] = longitude
    frame["latitude"] = latitude
    top_codes = frame["Code"].value_counts().head(5).index
    frame["Code_group"] = frame["Code"].where(frame["Code"].isin(top_codes), "Other / rare")
    frame["row_number"] = range(1, len(frame) + 1)
    return frame


def duplicate_audit(frame: pd.DataFrame) -> tuple[dict[str, int], pd.DataFrame]:
    comparison_columns = ["ID", "Northing", "Easting", "Elevation", "Code"]
    exact_mask = frame.duplicated(subset=comparison_columns, keep=False)
    coordinate_mask = frame.duplicated(subset=["Easting", "Northing"], keep=False)
    valid_ids = frame["ID"].fillna("").astype(str).str.strip().ne("")
    id_mask = valid_ids & frame.duplicated(subset=["ID"], keep=False)

    reasons = pd.Series("", index=frame.index, dtype="string")
    for mask, label in [
        (exact_mask, "Exact row"),
        (id_mask, "Repeated ID"),
        (coordinate_mask, "Repeated coordinates"),
    ]:
        reasons.loc[mask] = reasons.loc[mask].apply(
            lambda current: f"{current}; {label}" if current else label
        )

    report_columns = ["row_number", *comparison_columns, "latitude", "longitude"]
    report = frame.loc[reasons.ne(""), report_columns].copy()
    report.insert(1, "Duplicate_reason", reasons.loc[reasons.ne("")])
    counts = {
        "exact_rows": int(exact_mask.sum()),
        "repeated_id_rows": int(id_mask.sum()),
        "repeated_coordinate_rows": int(coordinate_mask.sum()),
        "flagged_rows": int(reasons.ne("").sum()),
    }
    return counts, report


def map_figure(data: pd.DataFrame, colour_by: str, basemap: str) -> go.Figure:
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
            color_continuous_scale=[
                [0.0, "#153D57"], [0.35, "#1F7A8C"],
                [0.7, "#74A98D"], [1.0, "#F0B44D"],
            ],
            hover_name="ID",
            hover_data=hover,
            zoom=INITIAL_MAP_ZOOM,
            height=525,
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
            zoom=INITIAL_MAP_ZOOM,
            height=525,
        )
        fig.update_layout(legend_title_text="Feature code")

    fig.update_traces(marker={"size": 9, "opacity": 0.88})
    map_layout = {
        "style": "open-street-map" if basemap == "OpenStreetMap" else "carto-positron",
        "center": {
            "lat": float(data["latitude"].mean()),
            "lon": float(data["longitude"].mean()),
        },
        "zoom": INITIAL_MAP_ZOOM,
    }
    if basemap in ARCGIS_TILES:
        map_layout = {
            "style": "white-bg",
            "center": {
                "lat": float(data["latitude"].mean()),
                "lon": float(data["longitude"].mean()),
            },
            "zoom": INITIAL_MAP_ZOOM,
            "layers": [{
                "below": "traces",
                "sourcetype": "raster",
                "source": [ARCGIS_TILES[basemap]],
                "sourceattribution": "Tiles © Esri and contributors",
            }],
        }

    fig.update_layout(
        map=map_layout,
        dragmode="pan",
        uirevision="preserve-map-view",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor=CANVAS,
        font={"color": NAVY},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.01, "x": 0},
    )
    return fig


try:
    points = load_points(str(GEOJSON_PATH), GEOJSON_PATH.stat().st_mtime_ns)
except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
    st.error(f"Dashboard data could not be loaded: {exc}")
    st.info("Run `Rscript mumbai_survey_analysis.R` to regenerate the GIS outputs.")
    st.stop()

active_source = "Bundled survey · 31 Aug 2026"
upload_error = None
upload_duplicate_counts = None
upload_duplicate_report = None
pending_upload = st.session_state.get("uploaded_dataset")
if pending_upload is not None:
    try:
        points = load_uploaded_csv(pending_upload.getvalue())
        upload_duplicate_counts, upload_duplicate_report = duplicate_audit(points)
        active_source = pending_upload.name
    except (ValueError, UnicodeDecodeError, pd.errors.ParserError) as exc:
        upload_error = str(exc)

st.markdown(
    f'<div class="dashboard-hero"><div><div class="dashboard-title">Mumbai Survey Web Map</div>'
    f'<div class="dashboard-meta">{active_source} · {SOURCE_CRS} · {len(points):,} mapped records</div>'
    f'</div><div class="status-pill">● LIVE DATA</div></div><div class="hero-spacer"></div>',
    unsafe_allow_html=True,
)

filter_code, filter_elevation = st.columns([1, 1])
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
filter_colour, filter_basemap, filter_upload = st.columns([1, 1, 0.58])
with filter_colour:
    colour_by = st.selectbox("Map colouring", ["Elevation", "Feature code"])
with filter_basemap:
    basemap_label = st.selectbox(
        "Basemap",
        ["OpenStreetMap", "Light", "ArcGIS Imagery", "ArcGIS Topographic", "ArcGIS Streets"],
    )
with filter_upload:
    st.markdown("<div style='height:1.52rem'></div>", unsafe_allow_html=True)
    with st.popover("↥ Update CSV", use_container_width=True):
        st.file_uploader(
            "Survey CSV",
            type=["csv"],
            key="uploaded_dataset",
            help="Expected coordinates: WGS 84 / UTM Zone 43N (EPSG:32643).",
        )
        st.caption("Required: ID, Northing, Easting, Elevation, Code")
        if upload_error:
            st.error(upload_error)
        elif pending_upload is not None:
            st.success(f"Active: {pending_upload.name} ({len(points):,} valid rows)")
            if upload_duplicate_counts["flagged_rows"]:
                st.warning(
                    f"{upload_duplicate_counts['flagged_rows']:,} rows need review · "
                    f"Exact: {upload_duplicate_counts['exact_rows']:,} · "
                    f"Repeated IDs: {upload_duplicate_counts['repeated_id_rows']:,} · "
                    f"Repeated coordinates: {upload_duplicate_counts['repeated_coordinate_rows']:,}"
                )
                st.download_button(
                    "Download duplicate report",
                    data=upload_duplicate_report.to_csv(index=False).encode("utf-8"),
                    file_name="survey_duplicate_report.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                st.info("Duplicate check passed: no repeated rows, IDs, or coordinates.")
        if st.button("Use bundled dataset", use_container_width=True):
            st.session_state["uploaded_dataset"] = None
            st.rerun()

filtered = points.loc[
    (points["Code"].isin(selected_codes) if selected_codes else points.index == points.index)
    & points["Elevation"].between(selected_elevation[0], selected_elevation[1])
].copy()

if filtered.empty:
    st.warning("No survey points match the selected filters.")
    st.stop()

metric_cols = st.columns(5)
metric_cols[0].metric("Survey points", f"{len(filtered):,}")
metric_cols[1].metric("Codes", f"{filtered['Code'].nunique():,}")
metric_cols[2].metric("Min elevation", f"{filtered['Elevation'].min():.2f}")
metric_cols[3].metric("Median elev.", f"{filtered['Elevation'].median():.2f}")
metric_cols[4].metric("Max elevation", f"{filtered['Elevation'].max():.2f}")

map_col, diagnostic_col = st.columns([2.3, 1], vertical_alignment="top")
with map_col:
    st.subheader("Full survey extent")
    st.caption("Wheel zoom · Drag pan · Toolbar: zoom, reset, fullscreen, export")
    st.plotly_chart(
        map_figure(filtered, colour_by, basemap_label),
        config=MAP_CONFIG,
        key="survey_navigation_map",
    )

with diagnostic_col:
    st.subheader("Diagnostics")
    histogram = px.histogram(
        filtered,
        x="Elevation",
        nbins=24,
        color_discrete_sequence=[TEAL],
        labels={"Elevation": "Elevation (source units)", "count": "Survey points"},
    )
    histogram.update_layout(
        title="Elevation distribution",
        showlegend=False,
        height=245,
        margin={"l": 5, "r": 5, "t": 38, "b": 5},
        yaxis_title="Survey points",
        font={"size": 10},
        paper_bgcolor=CANVAS,
        plot_bgcolor=CANVAS,
    )
    histogram.update_xaxes(showgrid=False, linecolor="#CBD7DE", tickcolor="#CBD7DE")
    histogram.update_yaxes(gridcolor="#DCE5EA", zeroline=False, linecolor="#CBD7DE")
    st.plotly_chart(histogram)

    counts = filtered["Code"].value_counts().head(12).sort_values().rename_axis("Code").reset_index(name="Records")
    bars = px.bar(
        counts,
        x="Records",
        y="Code",
        orientation="h",
        color_discrete_sequence=[ORANGE],
        text="Records",
    )
    bars.update_layout(
        title="Most frequent feature codes",
        height=245,
        margin={"l": 5, "r": 15, "t": 38, "b": 5},
        font={"size": 10},
        paper_bgcolor=CANVAS,
        plot_bgcolor=CANVAS,
    )
    bars.update_xaxes(gridcolor="#DCE5EA", zeroline=False, linecolor="#CBD7DE")
    bars.update_yaxes(showgrid=False, linecolor="#CBD7DE")
    bars.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(bars)

    quality_counts, _ = duplicate_audit(points)
    st.caption(
        f"Complete: {len(points):,} · "
        f"Exact duplicate rows: {quality_counts['exact_rows']:,} · "
        f"Repeated IDs: {quality_counts['repeated_id_rows']:,} · "
        f"Repeated coordinates: {quality_counts['repeated_coordinate_rows']:,}"
    )

    detail_columns = ["ID", "Code", "Elevation", "Easting", "Northing", "latitude", "longitude"]
    detail = filtered[detail_columns].sort_values(["Code", "ID"], na_position="last")
    st.download_button(
        "Download filtered records",
        data=detail.to_csv(index=False).encode("utf-8"),
        file_name="mumbai_survey_filtered.csv",
        mime="text/csv",
    )
