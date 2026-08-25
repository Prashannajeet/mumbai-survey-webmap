# Mumbai Survey Web Map

Interactive Streamlit dashboard for the 23 August 2026 Mumbai/Kurla survey.
The spatial analysis and GIS exports are generated in R; Streamlit reads the
resulting GeoJSON for interactive exploration.

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

## Project files

- `mumbai_survey_analysis.R`: data checks, static maps, CRS transformation,
  GeoPackage and GeoJSON exports.
- `app.py`: Streamlit dashboard.
- `output/mumbai_survey_points.geojson`: dashboard-ready spatial dataset.
- `output/mumbai_survey_points.gpkg`: GIS-ready point layer in EPSG:32643.

## Dashboard capabilities

- Full-area interactive web map with elevation or feature-code colouring.
- OpenStreetMap, light, ArcGIS World Imagery, ArcGIS Topographic, and ArcGIS
  Streets basemaps.
- Mouse-wheel zoom, drag-to-pan, zoom in/out, reset, fullscreen, and PNG export
  controls with the map view preserved across dashboard reruns.
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
