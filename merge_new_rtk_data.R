source_dir <- "/Users/prashannajeet/Documents/Projects/Amit-Kurla/RTK KURLA TILL DATE  31-08-2026/KURLA DGPS DATA 27826sta Files/27826sta Files"
output_dir <- file.path(getwd(), "data", "rtk_31-08-2026")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

csv_files <- list.files(source_dir, pattern = "\\.csv$", full.names = TRUE, ignore.case = TRUE)

read_survey_csv <- function(path) {
  data <- read.csv(
    path,
    header = FALSE,
    stringsAsFactors = FALSE,
    fill = TRUE,
    check.names = FALSE,
    na.strings = c("", "NA")
  )
  if (ncol(data) != 5) return(NULL)

  names(data) <- c("ID", "Northing", "Easting", "Elevation", "Code")
  data$Source_file <- basename(path)
  data$Source_row <- seq_len(nrow(data))
  data
}

parts <- lapply(csv_files, read_survey_csv)
compatible <- !vapply(parts, is.null, logical(1))
excluded_files <- basename(csv_files[!compatible])
parts <- parts[compatible]

merged <- do.call(rbind, parts)
rownames(merged) <- NULL
merged$ID <- toupper(trimws(as.character(merged$ID)))
merged$Code <- toupper(trimws(as.character(merged$Code)))
for (column in c("Northing", "Easting", "Elevation")) {
  merged[[column]] <- suppressWarnings(as.numeric(merged[[column]]))
}

valid_mask <- complete.cases(merged[, c("Northing", "Easting", "Elevation")]) & merged$ID != ""
invalid_rows <- merged[!valid_mask, , drop = FALSE]
valid_rows <- merged[valid_mask, , drop = FALSE]

exact_key <- paste(
  valid_rows$ID,
  sprintf("%.4f", valid_rows$Northing),
  sprintf("%.4f", valid_rows$Easting),
  sprintf("%.4f", valid_rows$Elevation),
  valid_rows$Code,
  sep = "|"
)
coordinate_key <- paste(
  sprintf("%.4f", valid_rows$Northing),
  sprintf("%.4f", valid_rows$Easting),
  sep = "|"
)

exact_involved <- duplicated(exact_key) | duplicated(exact_key, fromLast = TRUE)
coordinate_involved <- duplicated(coordinate_key) | duplicated(coordinate_key, fromLast = TRUE)
exact_duplicate_report <- valid_rows[exact_involved, , drop = FALSE]
coordinate_duplicate_report <- valid_rows[coordinate_involved, , drop = FALSE]
deduplicated <- valid_rows[!duplicated(exact_key), , drop = FALSE]

source_summary <- data.frame(
  Source_file = vapply(parts, function(x) unique(x$Source_file), character(1)),
  Raw_rows = vapply(parts, nrow, integer(1)),
  stringsAsFactors = FALSE
)
source_summary <- source_summary[order(source_summary$Source_file), ]

quality_summary <- data.frame(
  Metric = c(
    "Compatible CSV files", "Excluded non-5-column CSV files", "Raw rows",
    "Valid rows", "Invalid rows", "Exact duplicate rows involved",
    "Additional exact duplicates", "Deduplicated valid rows",
    "Repeated-coordinate rows involved", "Unique coordinate pairs"
  ),
  Value = c(
    length(parts), length(excluded_files), nrow(merged), nrow(valid_rows),
    nrow(invalid_rows), sum(exact_involved), sum(duplicated(exact_key)),
    nrow(deduplicated), sum(coordinate_involved), length(unique(coordinate_key))
  )
)

write.csv(deduplicated, file.path(output_dir, "RTK_KURLA_MERGED_DEDUPLICATED_31-08-2026.csv"), row.names = FALSE, na = "")
write.csv(exact_duplicate_report, file.path(output_dir, "exact_duplicate_report.csv"), row.names = FALSE, na = "")
write.csv(coordinate_duplicate_report, file.path(output_dir, "repeated_coordinate_report.csv"), row.names = FALSE, na = "")
write.csv(invalid_rows, file.path(output_dir, "invalid_row_report.csv"), row.names = FALSE, na = "")
write.csv(source_summary, file.path(output_dir, "source_file_summary.csv"), row.names = FALSE)
write.csv(quality_summary, file.path(output_dir, "merge_quality_summary.csv"), row.names = FALSE)
writeLines(excluded_files, file.path(output_dir, "excluded_files.txt"))

cat("Merged", length(parts), "compatible files.\n")
cat("Valid rows:", nrow(valid_rows), "\n")
cat("Deduplicated valid rows:", nrow(deduplicated), "\n")
cat("Outputs:", output_dir, "\n")
