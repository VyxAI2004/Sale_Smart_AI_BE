from typing import Optional


class GroundingHandler:

    @staticmethod
    def create_search_tools(provider: str) -> Optional[list]:

        if provider.lower() in ["google", "gemini"]:

            from google.genai import types
            return [types.Tool(google_search=types.GoogleSearch())]

        return None
    
    @staticmethod
    def extract_grounding_metadata(llm_response) -> Optional[dict]:

        raw_response = llm_response.raw
        
        if hasattr(raw_response, 'candidates') and raw_response.candidates:
            candidate = raw_response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                metadata = candidate.grounding_metadata
                return {
                    "grounding_supports": len(metadata.grounding_supports) if hasattr(metadata, 'grounding_supports') else 0,
                    "search_entry_point": "Google Search was used" if hasattr(metadata, 'search_entry_point') else None
                }
        
        return None
