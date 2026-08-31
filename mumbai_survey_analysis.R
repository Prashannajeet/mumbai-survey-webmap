#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(ggplot2)
  library(viridis)
})

project_dir <- "/Users/prashannajeet/Documents/Projects/Amit-Kurla"
input_file <- file.path(project_dir, "data", "rtk_31-08-2026", "RTK_KURLA_MERGED_DEDUPLICATED_31-08-2026.csv")
output_dir <- file.path(project_dir, "output")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

# Confirmed source CRS: WGS 84 / UTM zone 43N (EPSG:32643).
source_epsg <- 32643
dem_resolution_m <- 2
dem_web_resolution_m <- 20

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
source_label <- basename(input_file)

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
    caption = paste("Source:", source_label, "| CRS: WGS 84 / UTM zone 43N (EPSG:32643)")
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
    caption = paste("Source:", source_label, "| CRS: WGS 84 / UTM zone 43N (EPSG:32643)")
  ) + theme_map

p_hist <- ggplot(valid_points, aes(Elevation)) +
  geom_histogram(bins = 30, fill = "#176B87", colour = "white", linewidth = 0.35) +
  labs(
    title = "Distribution of surveyed elevations",
    subtitle = sprintf("n = %s complete records", nrow(valid_points)),
    x = "Elevation (source units)", y = "Survey points",
    caption = paste("Source:", source_label)
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

  if (requireNamespace("mgcv", quietly = TRUE) && requireNamespace("terra", quietly = TRUE)) {
    dem_model <- mgcv::gam(
      Elevation ~ s(Easting, Northing, bs = "tp", k = min(200, nrow(valid_points) - 1)),
      data = valid_points,
      method = "REML"
    )

    x_sequence <- seq(
      floor(min(valid_points$Easting) / dem_web_resolution_m) * dem_web_resolution_m,
      ceiling(max(valid_points$Easting) / dem_web_resolution_m) * dem_web_resolution_m,
      by = dem_web_resolution_m
    )
    y_sequence <- seq(
      floor(min(valid_points$Northing) / dem_web_resolution_m) * dem_web_resolution_m,
      ceiling(max(valid_points$Northing) / dem_web_resolution_m) * dem_web_resolution_m,
      by = dem_web_resolution_m
    )
    dem_grid <- expand.grid(Easting = x_sequence, Northing = y_sequence)

    survey_hull <- sf::st_convex_hull(sf::st_union(sf::st_geometry(survey_sf)))
    survey_footprint <- sf::st_buffer(survey_hull, dist = 40)
    grid_sf <- sf::st_as_sf(dem_grid, coords = c("Easting", "Northing"), crs = source_epsg, remove = FALSE)
    inside_footprint <- lengths(sf::st_within(grid_sf, survey_footprint)) > 0
    dem_grid <- dem_grid[inside_footprint, , drop = FALSE]

    predictions <- predict(dem_model, newdata = dem_grid, se.fit = TRUE)
    dem_grid$Elevation_DEM <- as.numeric(predictions$fit)
    dem_grid$Prediction_SE <- as.numeric(predictions$se.fit)

    dem_grid_sf <- sf::st_as_sf(
      dem_grid,
      coords = c("Easting", "Northing"),
      crs = source_epsg,
      remove = FALSE
    )
    dem_grid_wgs84 <- sf::st_transform(dem_grid_sf, 4326)
    dem_xy <- sf::st_coordinates(dem_grid_wgs84)
    dem_web <- bind_cols(
      sf::st_drop_geometry(dem_grid_wgs84),
      tibble(longitude = dem_xy[, 1], latitude = dem_xy[, 2])
    )
    write_csv(dem_web, file.path(output_dir, "mumbai_survey_dem_web.csv"))

    dem_raster <- terra::rast(
      xmin = floor(min(valid_points$Easting) / dem_resolution_m) * dem_resolution_m,
      xmax = ceiling(max(valid_points$Easting) / dem_resolution_m) * dem_resolution_m,
      ymin = floor(min(valid_points$Northing) / dem_resolution_m) * dem_resolution_m,
      ymax = ceiling(max(valid_points$Northing) / dem_resolution_m) * dem_resolution_m,
      resolution = dem_resolution_m,
      crs = paste0("EPSG:", source_epsg)
    )
    raster_xy <- terra::xyFromCell(dem_raster, seq_len(terra::ncell(dem_raster)))
    raster_predictions <- numeric(terra::ncell(dem_raster))
    prediction_chunks <- split(
      seq_len(terra::ncell(dem_raster)),
      ceiling(seq_len(terra::ncell(dem_raster)) / 50000)
    )
    for (cell_index in prediction_chunks) {
      raster_predictions[cell_index] <- predict(
        dem_model,
        newdata = data.frame(
          Easting = raster_xy[cell_index, 1],
          Northing = raster_xy[cell_index, 2]
        )
      )
    }
    terra::values(dem_raster) <- raster_predictions
    dem_raster <- terra::mask(dem_raster, terra::vect(survey_footprint), touches = TRUE)
    names(dem_raster) <- "Elevation_DEM"
    terra::writeRaster(
      dem_raster,
      file.path(output_dir, "mumbai_survey_dem_utm43n.tif"),
      overwrite = TRUE,
      gdal = c("COMPRESS=DEFLATE", "PREDICTOR=3")
    )

    dem_profile <- tibble(
      metric = c(
        "method", "source_crs", "resolution_m", "web_display_resolution_m",
        "raster_cells", "web_grid_cells",
        "minimum_dem_elevation", "mean_dem_elevation", "maximum_dem_elevation",
        "median_prediction_se"
      ),
      value = as.character(c(
        "Thin-plate regression spline (GAM REML)",
        "WGS 84 / UTM zone 43N (EPSG:32643)",
        dem_resolution_m, dem_web_resolution_m, terra::ncell(dem_raster), nrow(dem_grid),
        terra::global(dem_raster, "min", na.rm = TRUE)[1, 1],
        terra::global(dem_raster, "mean", na.rm = TRUE)[1, 1],
        terra::global(dem_raster, "max", na.rm = TRUE)[1, 1],
        median(dem_grid$Prediction_SE)
      ))
    )
    write_csv(dem_profile, file.path(output_dir, "dem_profile.csv"))
  } else {
    warning("Packages 'mgcv' and 'terra' are required to generate DEM outputs.")
  }
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
    dem = if (exists("dem_profile")) dem_profile else "DEM was not generated",
    session = sessionInfo()
  ),
  file = file.path(output_dir, "analysis_report.txt")
)

message("Analysis complete. Outputs written to: ", output_dir)
