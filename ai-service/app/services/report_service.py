# Coordinates the complete report generation workflow.
import logging
from app.services.dashboard_service import DashboardService
from app.services.rag_service import RagService
from app.rag.embeddings import EmbeddingGenerator
from app.rag.retrieval import retrieve_context
from app.llm.prompt_builder import build_prompt
from app.llm.llm_client import call_gemini
from app.llm.response_parser import parse_gemini_response
from app.report.report_generator import compile_report
from app.exceptions.custom_exception import ReportGenerationError, DatasetProcessingError, LLMError, EmbeddingError

logger = logging.getLogger("ai_service")

class ReportService:
    """
    Orchestrates the entire report compilation pipeline:
    1. Reads and cleans dataset.
    2. Compiles statistics and visual charts.
    3. Triggers vector database index initialization.
    4. Retrieves semantic row details matching user requirements.
    5. Feeds context to Gemini to compile advanced business analysis.
    6. Formats output into a cohesive HTML dashboard report.
    """
    @staticmethod
    async def generate_report(filename: str, file_bytes: bytes, prompt: str) -> dict:
        """
        Processes dataset and prompt query to output a complete analytical report.
        All operations run in-memory; results are returned directly.
        """
        logger.info(f"Initiating report generation for file '{filename}' with prompt: '{prompt}'")

        try:
            # Step 1: Preprocess dataset, run descriptive statistics, and recommend charts
            processed_data = DashboardService.process_dataset(filename, file_bytes)
            cleaned_df = processed_data["cleaned_df"]
            stats = processed_data["statistics"]
            charts = processed_data["charts"]

            # Step 2: Initialize index database mapping dataset rows to ChromaDB
            rag_service = RagService()
            rag_service.build_rag_pipeline(dataset_id=filename, df=cleaned_df)

            # Step 3: Embed user prompt query and perform vector similarity query
            emb_gen = EmbeddingGenerator()
            query_embedding = emb_gen.get_embedding(prompt)
            
            retrieved_context = retrieve_context(
                dataset_id=filename,
                query_text=prompt,
                query_embedding=query_embedding,
                top_k=10
            )

            # Step 4: Construct custom context analysis instructions prompt for LLM
            llm_prompt = build_prompt(
                user_prompt=prompt,
                stats=stats,
                retrieved_chunks=retrieved_context
            )

            # Step 5: Send prompt to Gemini for analytical summary compilation
            # Use lower temperature (0.15) to maintain professional grounded outputs
            raw_ai_analysis = await call_gemini(
                prompt=llm_prompt,
                model_name="gemini-3.6-flash",
                temperature=0.15
            )

            # Step 6: Parse the Markdown response into structured HTML analysis blocks
            ai_insights = parse_gemini_response(raw_ai_analysis)

            # Step 7: Combine stats, interactive Plotly charts, and AI analysis into a single document
            compiled_report = compile_report(
                dataset_id=filename,
                stats=stats,
                charts=charts,
                ai_insights=ai_insights
            )

            logger.info("Report generation workflow completed successfully.")
            return compiled_report

        except (DatasetProcessingError, EmbeddingError, LLMError) as exc:
            # Reraise custom exceptions directly
            raise
        except Exception as e:
            logger.error(f"Unexpected error during report generation: {e}", exc_info=True)
            raise ReportGenerationError(f"Complete report generation workflow failed: {str(e)}")