# Combines user requests, statistics and retrieved context into structured prompts.
import json

# stats: by statistics.py and retrieved chunks: by retrival.py
def build_prompt(user_prompt: str, stats: dict, retrieved_chunks: list[dict]) -> str:
    """
    Assembles a comprehensive LLM instruction prompt.
    Merges:
    1. Dataset profile metadata (dimensions, numeric/categorical column lists).
    2. Descriptive summary statistics.
    3. Contextual row snippets retrieved via RAG representing the user's specific interests.
    4. The user's query prompt.
    Generates strict instructions for structured Markdown sections.
    """
    # Extract dimensions and classifications
    shape = stats.get("shape", [0, 0])
    num_cols = stats.get("numerical_columns", [])
    cat_cols = stats.get("categorical_columns", [])
    
    # Compress numerical descriptive stats for LLM context size optimization
    simplified_numerical_stats = {}
    for col, metrics in stats.get("numerical_stats", {}).items():
        simplified_numerical_stats[col] = {
            "mean": metrics.get("mean"),
            "median": metrics.get("median"),
            "min": metrics.get("min"),
            "max": metrics.get("max")
        }

    # Format the RAG context chunks
    formatted_chunks = []
    if retrieved_chunks:
        for idx, chunk in enumerate(retrieved_chunks):
            # Print similarity score along with content to allow LLM to weigh context relevance
            formatted_chunks.append(
                f"Datapoint {idx + 1} (Relevance Score: {1.0 - chunk.get('distance', 0.0):.4f}):\n{chunk.get('text', '')}"
            )
        rag_context_str = "\n\n".join(formatted_chunks)
    else:
        rag_context_str = "No specific row-level context was retrieved."

    # Construct the instruction prompt
    prompt = f"""
You are an expert Data Scientist and Business Intelligence consultant. Analyze the following preprocessed dataset and address the user's query with a professional report.

### SECTION 1: DATASET PROFILE
- **Dimensions**: {shape[0]} rows, {shape[1]} columns.
- **Numerical Columns**: {", ".join(num_cols) if num_cols else "None"}
- **Categorical Columns**: {", ".join(cat_cols) if cat_cols else "None"}

### SECTION 2: STATISTICAL METRICS OVERVIEW
Below is the descriptive statistical profile computed for the numerical features:
{json.dumps(simplified_numerical_stats, indent=2)}

### SECTION 3: RELEVANT DATAPOINTS (RETRIEVED VIA RAG)
The following rows are semantically closest to the user's prompt:
{rag_context_str}

### SECTION 4: USER ANALYSIS REQUEST
The user wants to analyze this dataset with the following focus:
"{user_prompt}"

### SECTION 5: REPORT FORMATTING AND STRUCTURE RULES
Please compile a comprehensive, data-driven report structured exactly as follows. Use standard Markdown syntax. Do NOT output HTML tags directly.

1. **Title**: A professional and engaging report title. Use `# [Title]`
2. **Executive Summary**: A concise 1-2 paragraph description summarizing the scope, main findings, and data characteristics. Use `## Executive Summary`
3. **Detailed Analysis**: Address the user's request. Deep dive into the numbers, explain trends, cite specific row details from Section 3, and explain correlations. You are encouraged to present data in structured Markdown tables. Use `## Detailed Analysis`
4. **Key Insights & Anomalies**: Bullet points outlining core take-aways, outliers, or intriguing patterns. Use `## Key Insights & Anomalies`
5. **Recommendations**: 3-4 actionable business recommendations based on the findings. Use `## Strategic Recommendations`

Ensure the tone is analytical, executive-friendly, objective, and precise.
"""
    return prompt

"""
Complete workflow 
CSV

↓

Pandas

↓

Statistics

↓

Embeddings

↓

ChromaDB

↓

User Prompt

↓

Retriever

↓

Relevant Rows

↓

Prompt Builder

↓

One Large Prompt

↓

Gemini

↓

Markdown Report

↓

HTML/PDF Generator
"""