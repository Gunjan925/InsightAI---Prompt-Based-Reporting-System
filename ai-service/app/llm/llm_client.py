# Sends prompts to Gemini and returns generated responses.
import logging
import google.generativeai as genai
from app.config.settings import settings
from app.exceptions.custom_exception import LLMError

# Get the standard logging instance for the AI service
logger = logging.getLogger("ai_service")

# Module-level variable to cache whether the Gemini SDK has been initialized
# This configuration only needs to happen once during the application's lifetime.Without the flag, every request would execute: genai.configure(api_key=settings.GEMINI_API_KEY) again and again.
_gemini_sdk_configured = False

def _configure_gemini_sdk() -> None:
    """
    Configures the google-generativeai SDK with the user's API Key.
    Performs configuration only once per service lifecycle.
    Raises LLMError if the key is missing or invalid.
    """
    global _gemini_sdk_configured
    if not _gemini_sdk_configured:
        # Check if the API key has been supplied or if it's still default placeholder
        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key.strip() in ("", "your_gemini_api_key_here"):
            logger.warning("GEMINI_API_KEY is empty. The model cannot execute queries.")
            raise LLMError("Google Gemini API key is missing. Please configure GEMINI_API_KEY in the .env file.")

        try:
            logger.info("Initializing Google Generative AI SDK client instance.")
            genai.configure(api_key=api_key)
            _gemini_sdk_configured = True
            logger.info("Google Generative AI SDK configured successfully.")
        except Exception as e:
            logger.error(f"Error while configuring Generative AI SDK client: {e}")
            raise LLMError(f"Failed to configure Generative AI SDK credentials: {str(e)}")

async def call_gemini(prompt: str, model_name: str = "gemini-1.5-flash", temperature: float = 0.2) -> str:
    """
    Sends the compiled analysis prompt to the Google Gemini model asynchronously.
    
    Parameters:
    - prompt (str): The final, formatted prompt string containing dataset context, stats, and task instructions.
    - model_name (str): The specific model ID to call (defaults to 'gemini-1.5-flash' for optimal balance of speed/quality).
    - temperature (float): Sampling temperature (0.0 to 1.0) controlling variability (default 0.2 keeps responses logical).

    Returns:
    - str: The generated analysis text returned by the model.

    Raises:
    - LLMError: If any API error, timeout, or safety block prevents output generation.
    """
    # Verify/configure the SDK environment
    _configure_gemini_sdk()

    try:
        logger.info(f"Forwarding async generation request to Gemini model '{model_name}' (temp={temperature}).")
        
        # Instantiate the model client with specific configuration parameters
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"temperature": temperature}
        )

        # Call the async model generation endpoint to prevent blocking FastAPI's event loop thread
        response = await model.generate_content_async(prompt)
        
        # Verify response payload
        if not response.text:
            logger.error("Gemini returned an empty text field or the response was filtered out.")
            raise LLMError("Gemini generated an empty text response. This might be due to safety filters.")

        logger.info("Successfully received text completion back from Gemini.")
        return response.text

    except genai.types.generation_types.BlockedPromptException as bpe:
        logger.error(f"Gemini prompt generation blocked by safety filters: {bpe}")
        raise LLMError("The report generation prompt was flagged and blocked by Gemini's safety guidelines.")
    except Exception as e:
        logger.error(f"Exception encountered during Google Gemini API call execution: {str(e)}")
        raise LLMError(f"Gemini service communication error: {str(e)}")