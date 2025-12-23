import os
import google.generativeai as genai


def get_client():
    """
    Returns a Gemini GenerativeModel instance (NOT the module).
    This is the ONLY correct way to use Gemini with Streamlit Cloud.
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={
            "temperature": 0.0,
            "top_p": 1.0,
            "top_k": 1,
            "max_output_tokens": 2048,
        },
    )

    return model