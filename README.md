# Mumbai Survey Web Map

Interactive Streamlit dashboard for the Mumbai/Kurla survey updated through
31 August 2026.
The spatial analysis and GIS exports are generated in R; Streamlit reads the
resulting GeoJSON for interactive exploration.

## Deploy online with Streamlit

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in
   with GitHub.
2. Select **Create app** and choose this GitHub repository.
3. Set the branch to `main` and the entrypoint to `app.py`.
4. Select **Deploy**. No secrets or external database are required.

The committed GeoJSON is the default online dataset. The **Update CSV** tool
supports temporary browser-session updates; uploaded data is not written back
to GitHub or retained after the session ends.

## Coordinate system

The confirmed source CRS is **WGS 84 / UTM Zone 43N (EPSG:32643)**. The R
pipeline exports a WGS 84 GeoJSON for browser mapping.

## Run locally

```bash
Rscript mumbai_survey_analysis.R
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Open <http://localhost:8501>.

The R analysis requires `readr`, `dplyr`, `ggplot2`, `viridis`, `sf`, `mgcv`,
and `terra`. The Streamlit deployment uses the committed web DEM and does not
need R at runtime.

## Project files

- `mumbai_survey_analysis.R`: data checks, static maps, CRS transformation,
  GeoPackage and GeoJSON exports.
- `app.py`: Streamlit dashboard.
- `data/rtk_31-08-2026/RTK_KURLA_MERGED_DEDUPLICATED_31-08-2026.csv`:
  validated bundled source containing 2,611 unique survey records.
- `output/mumbai_survey_points.geojson`: dashboard-ready spatial dataset.
- `output/mumbai_survey_points.gpkg`: GIS-ready point layer in EPSG:32643.
- `output/mumbai_survey_dem_utm43n.tif`: interpolated GeoTIFF DEM in EPSG:32643.
- `output/mumbai_survey_dem_web.csv`: web-map grid with WGS 84 coordinates.

## Dashboard capabilities

- Full-area interactive web map with elevation or feature-code colouring.
- Smooth 2 m DEM generated in R with a thin-plate regression spline, available
  as points-only, DEM-plus-points, and DEM-only map views. The browser uses a
  20 m display sample for responsive interaction while the downloadable
  GeoTIFF retains the full 2 m resolution. The interpolation is clipped to a
  buffered survey footprint to limit unsupported extrapolation.
- OpenStreetMap, light, ArcGIS World Imagery, ArcGIS Topographic, and ArcGIS
  Streets basemaps.
- Mouse-wheel zoom, drag-to-pan, zoom in/out, reset, fullscreen, and PNG export
  controls with the map view preserved across dashboard reruns. The initial
  view includes wider surrounding context and zoom-out is not restricted to
  the survey bounds.
- Feature-code and elevation filters shared across the dashboard.
- Elevation distribution and feature-code ranking.
- Data-quality guardrails and downloadable filtered records.
- Fixed single-screen canvas with no page scrolling, sidebar, or tab frames.
- Map and diagnostic charts remain visible together; filtered records are
  available as a CSV download.
- Professional civic-GIS visual system with a navy, teal, and gold palette,
  polished KPI cards, coordinated charts, and a high-contrast map tool dock.
- In-app CSV updates without restarting the dashboard. Uploaded files require
  `ID`, `Northing`, `Easting`, `Elevation`, and `Code`; coordinates are treated
  as EPSG:32643 and transformed for web mapping in memory. The bundled survey
  can be restored from the same tool.
- Automatic upload duplicate checks for exact rows, repeated IDs, and repeated
  coordinate pairs, with a downloadable CSV report of all flagged records.
