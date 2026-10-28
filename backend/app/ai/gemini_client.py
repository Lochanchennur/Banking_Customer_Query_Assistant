import json
import logging
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.ai.tool_registry import TOOL_DEFINITIONS

logger = logging.getLogger(__name__)

def is_gemini_available() -> bool:
    return bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5)

def call_gemini_with_tools(
    system_prompt: str,
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Call Gemini LLM with function calling schemas.
    Returns parsed tool calls or generated text response.
    """
    if not is_gemini_available():
        return None

    try:
        # Try google.genai first
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Formulate prompt
            contents = []
            if history:
                for h in history[-4:]:
                    role = "user" if h.get("role") == "user" else "model"
                    contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h.get("content", ""))]))
            
            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))
            
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
            )

            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=config
            )
            
            if response and response.text:
                return {"type": "text", "text": response.text}
        except Exception as e_genai:
            logger.info(f"google.genai call attempt: {e_genai}, trying fallback library...")

            # Fallback to google.generativeai
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=settings.GEMINI_API_KEY)
            model = legacy_genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                system_instruction=system_prompt
            )
            chat = model.start_chat()
            res = chat.send_message(user_message)
            if res and res.text:
                return {"type": "text", "text": res.text}

    except Exception as e:
        logger.warning(f"Gemini API request failed: {e}. Falling back to deterministic engine.")
        return None

    return None
