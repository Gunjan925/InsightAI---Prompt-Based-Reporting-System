# Stores reusable constants and application-wide configuration values.

# Acceptable structured dataset file formats
SUPPORTED_EXTENSIONS = {".csv", ".xls", ".xlsx"}

# Visual system color tokens (Indigo, Teal, Rose, Amber, Emerald, Slate) for matching chart palettes
CHART_COLORS = [
    "#6366f1",  # Indigo 500 (Primary)
    "#06b6d4",  # Teal 500 (Secondary)
    "#ec4899",  # Rose 500 (Accent)
    "#f59e0b",  # Amber 500
    "#10b981",  # Emerald 500
    "#8b5cf6"   # Violet 500
]

# Standard RAG parameters
DEFAULT_RETRIEVAL_K = 10

# Maximum dataset size threshold in bytes (e.g., 15MB)
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024