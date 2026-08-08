import logging
import httpx
from fastapi import HTTPException, status
from app.config.settings import settings

logger = logging.getLogger("app")

# Defines a client responsible for communicating with the AI Service.
class AiClient:
    @staticmethod
    async def generate_report_from_ai_service(
        filename: str,
        file_content: bytes,
        mime_type: str,
        prompt: str
    ) -> dict:
        """
        Sends the dataset file binary and user analysis prompt to the external AI Service,
        and retrieves the generated report title, summary, and HTML/Markdown content.
        """
        # Endpoint in the AI service folder/application
        url = f"{settings.AI_SERVICE_URL.rstrip('/')}/api/generate" # rstrip('/') removes the ending /
        logger.info(f"Forwarding report generation request to AI Service at: {url}")
        
        # Format the file and prompt payload as multipart/form-data
        files = {
            "file": (filename, file_content, mime_type)
        }
        data = {
            "prompt": prompt
        }
        
        try:
            async with httpx.AsyncClient(timeout=180.0) as client: # Creates an asynchronous HTTP client. timeout=180 means Wait up to 180 seconds (3 minutes) for the AI Service.
                response = await client.post(url, files=files, data=data) # Sends an HTTP POST request.
                
            if response.status_code != 200:
                logger.error(f"AI Service returned non-200 code: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"AI Service error: {response.text}"
                )
                
            report_data = response.json() # Converts JSON received from the AI Service into a Python dictionary.
            logger.info("Successfully received report content from the AI Service.")
            
            return {
                "report_title": report_data.get("report_title", f"AI Generated Report - {filename}"),
                "summary": report_data.get("summary", "Analysis report generated successfully."),
                "content": report_data.get("content", "<h1>No report content returned by AI Service.</h1>")
            }

        # Runs if , AI Service is not running , Wrong port , Server unreachable.    
        except httpx.ConnectError as ce:
            logger.error(f"Could not connect to AI Service at {url}: {ce}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Connection to AI Service failed. Please ensure the AI service is online and running."
            )
        except Exception as e: # Handles all unexpected errors.
            logger.error(f"Unhandled error during AI service API call: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error contacting AI Service: {str(e)}"
            )

    @staticmethod
    async def generate_dashboard_from_ai_service(
        filename: str,
        file_content: bytes,
        mime_type: str
    ) -> dict:
        """
        Forwards the dataset binary to the AI Service's /api/dashboard endpoint.
        The AI Service reads, cleans, and statistically profiles the dataset, then recommends and generates Plotly charts — all WITHOUT calling any LLM.
        Returns: { dataset_id, row_count, col_count, columns, charts }
        """
        url = f"{settings.AI_SERVICE_URL.rstrip('/')}/api/dashboard"
        logger.info(f"Forwarding dashboard generation request to AI Service at: {url}")

        # Send file as multipart/form-data — no prompt needed for dashboard
        files = {
            "file": (filename, file_content, mime_type)
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, files=files)

            if response.status_code != 200:
                logger.error(f"AI Service dashboard error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"AI Service dashboard error: {response.text}"
                )

            dashboard_data = response.json()
            logger.info("Successfully received dashboard data from AI Service.")
            return dashboard_data

        except httpx.ConnectError as ce:
            logger.error(f"Could not connect to AI Service for dashboard at {url}: {ce}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Connection to AI Service failed. Please ensure the AI service is online and running."
            )
        except Exception as e:
            logger.error(f"Unhandled error during AI service dashboard API call: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error contacting AI Service for dashboard: {str(e)}"
            )
