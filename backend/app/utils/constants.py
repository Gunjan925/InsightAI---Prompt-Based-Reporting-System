# storing all the validations constants that should be checked while the user data is uploaded

# Supported file formats and size constraints
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

ALLOWED_MIME_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}

# 10 MB maximum file size limit in bytes
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024