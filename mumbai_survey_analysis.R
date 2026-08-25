#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(ggplot2)
  library(viridis)
})

input_file <- "/Users/prashannajeet/Documents/Projects/Amit-Kurla/23-08-2026 TOTAL.csv"
output_dir <- "/Users/prashannajeet/Documents/Flood/output"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

# Confirmed source CRS: WGS 84 / UTM zone 43N (EPSG:32643).
source_epsg <- 32643

survey <- read_csv(
  input_file,
  col_types = cols(
    ID = col_character(),
    Northing = col_double(),
    Easting = col_double(),
    Elevation = col_double(),
    Code = col_character()
  ),
  trim_ws = TRUE,
  show_col_types = FALSE
) %>%
  mutate(
    ID = trimws(ID),
    Code = toupper(trimws(Code)),
    row_number = row_number()
  )

required <- c("ID", "Northing", "Easting", "Elevation", "Code")
stopifnot(all(required %in% names(survey)))

valid_points <- survey %>%
  filter(is.finite(Easting), is.finite(Northing), is.finite(Elevation))

top_codes <- survey %>% count(Code, sort = TRUE) %>% slice_head(n = 5) %>% pull(Code)
valid_points <- valid_points %>%
  mutate(Code_group = if_else(Code %in% top_codes, Code, "Other / rare"))

profile <- tibble(
  metric = c(
    "rows", "columns", "complete coordinate/elevation rows",
    "exact duplicate rows", "duplicate nonblank IDs",
    "duplicate coordinate pairs", "distinct codes",
    "minimum easting_m", "maximum easting_m", "easting span_m",
    "minimum northing_m", "maximum northing_m", "northing span_m",
    "minimum elevation", "median elevation", "mean elevation",
    "maximum elevation", "elevation IQR"
  ),
  value = c(
    nrow(survey), ncol(survey), nrow(valid_points),
    sum(duplicated(survey[required])),
    sum(duplicated(survey$ID) & !is.na(survey$ID) & survey$ID != ""),
    sum(duplicated(survey[c("Easting", "Northing")])),
    n_distinct(survey$Code, na.rm = TRUE),
    min(valid_points$Easting), max(valid_points$Easting), diff(range(valid_points$Easting)),
    min(valid_points$Northing), max(valid_points$Northing), diff(range(valid_points$Northing)),
    min(valid_points$Elevation), median(valid_points$Elevation), mean(valid_points$Elevation),
    max(valid_points$Elevation), IQR(valid_points$Elevation)
  )
)

missingness <- tibble(
  field = required,
  missing_count = vapply(survey[required], function(x) sum(is.na(x) | (is.character(x) & trimws(x) == "")), numeric(1)),
  missing_percent = 100 * missing_count / nrow(survey)
)

code_summary <- survey %>%
  mutate(Code = if_else(is.na(Code) | Code == "", "(missing)", Code)) %>%
  count(Code, name = "records", sort = TRUE) %>%
  mutate(percent = 100 * records / sum(records))

elevation_summary <- valid_points %>%
  summarise(
    n = n(), min = min(Elevation), q1 = quantile(Elevation, 0.25),
    median = median(Elevation), mean = mean(Elevation),
    q3 = quantile(Elevation, 0.75), max = max(Elevation), sd = sd(Elevation)
  )

write_csv(profile, file.path(output_dir, "data_quality_profile.csv"))
write_csv(missingness, file.path(output_dir, "missingness.csv"))
write_csv(code_summary, file.path(output_dir, "code_summary.csv"))
write_csv(elevation_summary, file.path(output_dir, "elevation_summary.csv"))

theme_map <- theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(face = "bold", colour = "#17212B"),
    plot.subtitle = element_text(colour = "#52606D"),
    panel.grid.minor = element_blank(),
    legend.position = "right"
  )

p_elevation <- ggplot(valid_points, aes(Easting, Northing, colour = Elevation)) +
  geom_point(size = 2.2, alpha = 0.9) +
  scale_colour_viridis_c(option = "C", name = "Elevation") +
  coord_equal(expand = TRUE) +
  labs(
    title = "Mumbai survey points by elevation",
    subtitle = sprintf("%s valid points; projected coordinates shown in metres", nrow(valid_points)),
    x = "Easting (m)", y = "Northing (m)",
    caption = "Source: 23-08-2026 TOTAL.csv | CRS: WGS 84 / UTM zone 43N (EPSG:32643)"
  ) + theme_map

p_code <- ggplot(valid_points, aes(Easting, Northing, colour = Code_group)) +
  geom_point(size = 2.2, alpha = 0.88) +
  scale_colour_manual(
    values = c("FT" = "#176B87", "LV" = "#D98E04", "CH" = "#7C8C3C",
               "ROAD LV" = "#B44C72", "CHTOP" = "#68478D", "Other / rare" = "#A7AFB7"),
    name = "Code group"
  ) +
  coord_equal(expand = TRUE) +
  labs(
    title = "Mumbai survey points by feature code",
    subtitle = "Five most frequent codes shown separately; remaining codes grouped",
    x = "Easting (m)", y = "Northing (m)",
    caption = "Source: 23-08-2026 TOTAL.csv | CRS: WGS 84 / UTM zone 43N (EPSG:32643)"
  ) + theme_map

p_hist <- ggplot(valid_points, aes(Elevation)) +
  geom_histogram(bins = 30, fill = "#176B87", colour = "white", linewidth = 0.35) +
  labs(
    title = "Distribution of surveyed elevations",
    subtitle = sprintf("n = %s complete records", nrow(valid_points)),
    x = "Elevation (source units)", y = "Survey points",
    caption = "Source: 23-08-2026 TOTAL.csv"
  ) + theme_map

ggsave(file.path(output_dir, "survey_elevation_map.png"), p_elevation, width = 10, height = 8, dpi = 220, bg = "white")
ggsave(file.path(output_dir, "survey_code_map.png"), p_code, width = 10, height = 8, dpi = 220, bg = "white")
ggsave(file.path(output_dir, "elevation_distribution.png"), p_hist, width = 9, height = 6, dpi = 220, bg = "white")

if (requireNamespace("sf", quietly = TRUE)) {
  survey_sf <- sf::st_as_sf(valid_points, coords = c("Easting", "Northing"), crs = source_epsg, remove = FALSE)
  survey_wgs84 <- sf::st_transform(survey_sf, 4326)
  sf::st_write(survey_sf, file.path(output_dir, "mumbai_survey_points.gpkg"), layer = "survey_points", delete_dsn = TRUE, quiet = TRUE)
  sf::st_write(survey_wgs84, file.path(output_dir, "mumbai_survey_points.geojson"), delete_dsn = TRUE, quiet = TRUE)
  xy <- sf::st_coordinates(survey_wgs84)
  write_csv(bind_cols(sf::st_drop_geometry(survey_wgs84), tibble(longitude = xy[, 1], latitude = xy[, 2])),
            file.path(output_dir, "survey_points_wgs84.csv"))
} else {
  warning("Package 'sf' is unavailable: GeoPackage, GeoJSON, and WGS84 CSV were not created.")
}

capture.output(
  list(
    input = input_file,
    source_crs = "WGS 84 / UTM zone 43N (EPSG:32643; confirmed by user)",
    profile = profile,
    missingness = missingness,
    codes = code_summary,
    elevation = elevation_summary,
    session = sessionInfo()
  ),
  file = file.path(output_dir, "analysis_report.txt")
)

message("Analysis complete. Outputs written to: ", output_dir)
