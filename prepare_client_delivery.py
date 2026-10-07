from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT / "Final_Deliverable_Kurla_2026-10-05_A1"


FILES = [
    ("deliverables/Kurla_Topographical_Survey_Report_Final.docx", "report/Kurla_Topographical_Survey_Report_Final.docx", "Final topographical survey report", "Document", "Not applicable"),
    ("data/rtk_01-10-2026/RTK_KURLA_FINAL_UPDATED_01-10-2026.csv", "data/survey/Kurla_Final_Survey_Points_UTM43N.csv", "Final survey point register with 4,125 records", "CSV", "EPSG 32643"),
    ("data/Additional data 01 Oct 2026.csv", "data/source/Additional data 01 Oct 2026.csv", "Additional drainage survey received 1 October 2026", "CSV", "EPSG 32643"),
    ("data/rtk_01-10-2026/integration_summary.csv", "data/survey/integration_summary.csv", "Survey consolidation summary", "CSV", "Not applicable"),
    ("data/rtk_01-10-2026/coincident_observation_update_log.csv", "data/survey/coincident_observation_update_log.csv", "Coincident observation traceability register", "CSV", "EPSG 32643"),
    ("Survey/KURLA STATIC SURVEY ( TBM POLINT LIST).xlsx", "data/control/Kurla_BM_TBM_Control.xlsx", "BM and TBM control workbook", "XLSX", "EPSG 32643"),
    ("data/site_photos/photo_evidence_manifest.csv", "data/site_photos/photo_evidence_manifest.csv", "Geotagged photographic evidence register", "CSV", "EPSG 4326"),
    ("output/mumbai_survey_points.gpkg", "output/mumbai_survey_points.gpkg", "Survey point GIS layer for engineering use", "GeoPackage", "EPSG 32643"),
    ("output/mumbai_survey_points.geojson", "output/mumbai_survey_points.geojson", "Survey point layer for web mapping", "GeoJSON", "EPSG 4326"),
    ("output/survey_points_wgs84.csv", "output/survey_points_wgs84.csv", "Survey point table for geographic applications", "CSV", "EPSG 4326"),
    ("output/mumbai_survey_dem_utm43n.tif", "output/mumbai_survey_dem_utm43n.tif", "Two metre digital elevation model", "GeoTIFF", "EPSG 32643"),
    ("output/mumbai_survey_dem_web.csv", "output/mumbai_survey_dem_web.csv", "Optimised DEM layer for dashboard display", "CSV", "EPSG 4326"),
    ("output/mumbai_survey_dsm_utm43n.tif", "output/mumbai_survey_dsm_utm43n.tif", "Two metre survey-derived digital surface model", "GeoTIFF", "EPSG 32643"),
    ("output/mumbai_survey_dsm_web.csv", "output/mumbai_survey_dsm_web.csv", "Optimised DSM layer for dashboard display", "CSV", "EPSG 4326"),
    ("output/mumbai_survey_contours_utm43n.gpkg", "output/mumbai_survey_contours_utm43n.gpkg", "Half metre contours with two metre index classification", "GeoPackage", "EPSG 32643"),
    ("output/mumbai_survey_contours_wgs84.geojson", "output/mumbai_survey_contours_wgs84.geojson", "Contour layer for dashboard display", "GeoJSON", "EPSG 4326"),
    ("output/elevation_summary.csv", "output/elevation_summary.csv", "Survey elevation statistics", "CSV", "Not applicable"),
    ("output/code_summary.csv", "output/code_summary.csv", "Survey feature-code listing", "CSV", "Not applicable"),
    ("output/map_point_category_summary.csv", "output/map_point_category_summary.csv", "Map point-category summary derived from survey codes", "CSV", "Not applicable"),
    ("output/map_control_point_schedule.csv", "output/map_control_point_schedule.csv", "Control-point schedule used on the A1 maps", "CSV", "EPSG 32643"),
    ("output/dem_profile.csv", "output/dem_profile.csv", "DEM product specifications", "CSV", "EPSG 32643"),
    ("output/dsm_profile.csv", "output/dsm_profile.csv", "DSM product specifications", "CSV", "EPSG 32643"),
    ("output/survey_elevation_map.png", "maps/survey_elevation_map.png", "Survey elevation map", "PNG", "EPSG 32643"),
    ("output/survey_code_map.png", "maps/survey_code_map.png", "Survey feature-code map", "PNG", "EPSG 32643"),
    ("output/elevation_distribution.png", "maps/elevation_distribution.png", "Elevation distribution figure", "PNG", "Not applicable"),
    ("output/report_assets/dem_2m_final.png", "maps/dem_2m_final.png", "Two metre DEM figure", "PNG", "EPSG 32643"),
    ("output/report_assets/dsm_2m_final.png", "maps/dsm_2m_final.png", "Two metre DSM figure", "PNG", "EPSG 32643"),
    ("output/report_assets/contours_final.png", "maps/contours_final.png", "Contour figure", "PNG", "EPSG 32643"),
    ("output/report_assets/photo_evidence_map.png", "maps/photo_evidence_map.png", "Photographic evidence location map", "PNG", "EPSG 4326"),
    ("output/pdf/Kurla_A1_Site_Map_01_Topographic.pdf", "maps/A1/Kurla_A1_Site_Map_01_Topographic.pdf", "A1 topographic survey plan", "PDF", "EPSG 32643"),
    ("output/pdf/Kurla_A1_Site_Map_02_Satellite_Hybrid.pdf", "maps/A1/Kurla_A1_Site_Map_02_Satellite_Hybrid.pdf", "A1 satellite-hybrid survey plan", "PDF", "EPSG 32643"),
    ("deliverables/Kurla_Vector_Shapefiles_UTM43N.zip", "vectors/Kurla_Vector_Shapefiles_UTM43N.zip", "Seven-layer ESRI Shapefile package", "ZIP", "EPSG 32643 and EPSG 4326"),
    ("output/cross_sections/major_road_cross_sections_summary.csv", "output/cross_sections/major_road_cross_sections_summary.csv", "Five-section coordinate and level schedule", "CSV", "EPSG 32643"),
    ("output/cross_sections/major_road_cross_sections_profiles.csv", "output/cross_sections/major_road_cross_sections_profiles.csv", "Cross-section offset and reduced-level data", "CSV", "EPSG 32643"),
    ("output/cross_sections/major_road_cross_sections_field_points.csv", "output/cross_sections/major_road_cross_sections_field_points.csv", "Nearby survey observations for the section drawings", "CSV", "EPSG 32643"),
    ("output/cross_sections/major_road_cross_sections_utm43n.gpkg", "output/cross_sections/major_road_cross_sections_utm43n.gpkg", "Road axis and five cross-section lines", "GeoPackage", "EPSG 32643"),
    ("output/cross_sections/XS-01_profile.csv", "output/cross_sections/XS-01_profile.csv", "Cross-section schedule XS-01", "CSV", "EPSG 32643"),
    ("output/cross_sections/XS-02_profile.csv", "output/cross_sections/XS-02_profile.csv", "Cross-section schedule XS-02", "CSV", "EPSG 32643"),
    ("output/cross_sections/XS-03_profile.csv", "output/cross_sections/XS-03_profile.csv", "Cross-section schedule XS-03", "CSV", "EPSG 32643"),
    ("output/cross_sections/XS-04_profile.csv", "output/cross_sections/XS-04_profile.csv", "Cross-section schedule XS-04", "CSV", "EPSG 32643"),
    ("output/cross_sections/XS-05_profile.csv", "output/cross_sections/XS-05_profile.csv", "Cross-section schedule XS-05", "CSV", "EPSG 32643"),
    ("output/cross_sections/major_road_cross_sections_location_map.png", "maps/major_road_cross_sections_location_map.png", "Road cross-section location map", "PNG", "EPSG 32643"),
    ("output/cross_sections/major_road_cross_sections_profiles.png", "maps/major_road_cross_sections_profiles.png", "Combined five-section profile sheet", "PNG", "EPSG 32643"),
    ("output/cross_sections/XS-01_profile.png", "maps/cross_sections/XS-01_profile.png", "Individual cross-section drawing XS-01", "PNG", "EPSG 32643"),
    ("output/cross_sections/XS-02_profile.png", "maps/cross_sections/XS-02_profile.png", "Individual cross-section drawing XS-02", "PNG", "EPSG 32643"),
    ("output/cross_sections/XS-03_profile.png", "maps/cross_sections/XS-03_profile.png", "Individual cross-section drawing XS-03", "PNG", "EPSG 32643"),
    ("output/cross_sections/XS-04_profile.png", "maps/cross_sections/XS-04_profile.png", "Individual cross-section drawing XS-04", "PNG", "EPSG 32643"),
    ("output/cross_sections/XS-05_profile.png", "maps/cross_sections/XS-05_profile.png", "Individual cross-section drawing XS-05", "PNG", "EPSG 32643"),
    ("app.py", "app.py", "Streamlit survey dashboard", "Python", "Uses EPSG 4326 web layers"),
    ("requirements.txt", "requirements.txt", "Dashboard software requirements", "Text", "Not applicable"),
    (".streamlit/config.toml", ".streamlit/config.toml", "Streamlit display configuration", "TOML", "Not applicable"),
    ("README.md", "README.md", "Project and dashboard instructions", "Markdown", "Not applicable"),
    ("integrate_additional_survey_data.R", "scripts/integrate_additional_survey_data.R", "Additional survey integration workflow", "R", "EPSG 32643"),
    ("mumbai_survey_analysis.R", "scripts/mumbai_survey_analysis.R", "GIS analysis and product-generation workflow", "R", "EPSG 32643"),
    ("generate_report_surface_maps.R", "scripts/generate_report_surface_maps.R", "Report map-generation workflow", "R", "EPSG 32643"),
    ("generate_major_road_cross_sections.R", "scripts/generate_major_road_cross_sections.R", "Road cross-section generation workflow", "R", "EPSG 32643"),
    ("generate_a0_site_maps.R", "scripts/generate_a0_site_maps.R", "Professional A1 site-map generation workflow", "R", "EPSG 32643"),
    ("export_vector_shapefiles.R", "scripts/export_vector_shapefiles.R", "Vector Shapefile export workflow", "R", "EPSG 32643 and EPSG 4326"),
]


def copy_file(source: str, destination: str) -> None:
    src = ROOT / source
    dst = PACKAGE / destination
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def readable_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if PACKAGE.exists():
    shutil.rmtree(PACKAGE)
PACKAGE.mkdir(parents=True, exist_ok=True)

for generated_name in ("DELIVERY_README.md", "FILE_CHECKSUMS_SHA256.txt"):
    generated_path = PACKAGE / generated_name
    if generated_path.exists():
        generated_path.unlink()

for source, destination, _, _, _ in FILES:
    copy_file(source, destination)

for folder_name in ("web", "thumbnails"):
    source_folder = ROOT / "data" / "site_photos" / folder_name
    destination_folder = PACKAGE / "data" / "site_photos" / folder_name
    shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)

inventory = []
for path in sorted(PACKAGE.rglob("*")):
    if path.is_file():
        inventory.append((path.relative_to(PACKAGE).as_posix(), path.stat().st_size, checksum(path)))

rows = []
for _, destination, purpose, file_type, crs in FILES:
    path = PACKAGE / destination
    rows.append((destination, purpose, file_type, crs, readable_size(path.stat().st_size)))

web_count = len(list((PACKAGE / "data" / "site_photos" / "web").glob("*")))
thumb_count = len(list((PACKAGE / "data" / "site_photos" / "thumbnails").glob("*")))
package_size = sum(size for _, size, _ in inventory)

readme = [
    "# Kurla Topographical Survey Final Deliverable",
    "",
    "Delivery date: 5 October 2026",
    "",
    "Engineering coordinate system: WGS 84 UTM Zone 43N EPSG 32643",
    "",
    "Web mapping coordinate system: WGS 84 EPSG 4326",
    "",
    "## Package summary",
    "",
    "- Final survey observations: 4,125",
    "- BM and TBM control points listed in the report: 12",
    "- DEM resolution: 2 m",
    "- DSM resolution: 2 m",
    "- Contour interval: 0.5 m with 2 m index contours",
    "- Major-road cross sections: 5 sections at 200 m spacing",
    "- Professional A1 site-map sheets: 2",
    f"- Geotagged photographs: {web_count}",
    f"- Photograph thumbnails: {thumb_count}",
    f"- Combined package size: {readable_size(package_size)}",
    "",
    "## Data delivery listing",
    "",
    "| File | Description | Format | Coordinate system | Size |",
    "| --- | --- | --- | --- | ---: |",
]
for file_name, purpose, file_type, crs, size in rows:
    readme.append(f"| `{file_name}` | {purpose} | {file_type} | {crs} | {size} |")
readme.extend([
    "",
    "The `data/site_photos/web` folder contains the mapped site photographs. The `data/site_photos/thumbnails` folder supports quick dashboard display. Full file checksums are supplied in `FILE_CHECKSUMS_SHA256.txt`.",
    "",
    "## Running the dashboard",
    "",
    "From this folder, install the packages in `requirements.txt`, then run:",
    "",
    "```text",
    "streamlit run app.py",
    "```",
    "",
    "The dashboard reads its point, DEM, DSM, contour and photographic layers directly from the `output` and `data/site_photos` folders included here.",
])
(PACKAGE / "DELIVERY_README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

checksum_lines = [f"{digest}  {name}" for name, _, digest in inventory]
(PACKAGE / "FILE_CHECKSUMS_SHA256.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

print(PACKAGE)
print(f"Files: {len(inventory) + 2}")
print(f"Size: {readable_size(package_size)}")
