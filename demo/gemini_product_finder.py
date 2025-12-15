import os
import json
from typing import List, Dict, Any

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiProductFinder:
    def __init__(self, api_key: str = None):
        if not genai:
            raise ImportError("Please install google-generativeai: pip install google-generativeai")
        
        # Try to get API key from parameter, then env var, then env.py
        api_key_to_use = api_key
        
        if not api_key_to_use:
            # Try GEMINI_API_KEY or GOOGLE_API_KEY from environment
            api_key_to_use = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key_to_use:
            # Try to load from env.py
            try:
                from env import env
                api_key_to_use = getattr(env, 'GEMINI_API_KEY', None)
            except:
                pass
        
        if not api_key_to_use:
            raise ValueError(
                "GEMINI_API_KEY or GOOGLE_API_KEY not found. Please:\n"
                "1. Get your API key from https://aistudio.google.com/app/apikey\n"
                "2. Add GEMINI_API_KEY=your_key to .env file"
            )
            
        genai.configure(api_key=api_key_to_use)
        # Using gemini-1.5-flash instead of 2.0 because it has much higher free tier quota
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def find_products(self, query: str, product_context: List[Dict[str, Any]]) -> Dict[str, Any]:

        context_str = json.dumps(product_context[:50], default=str, ensure_ascii=False, indent=2) # Limit to 50 products for demo to avoid token limits
        
        prompt = f"""
You are a smart shopping assistant. Analyze the user's query and recommend the most suitable products from the available list.

User Query: "{query}"

Available Products (JSON):
{context_str}

Task:
1. Analyze what the user is looking for based on their query
2. Select the top 3-5 most relevant products from the list
3. Explain why each product matches the user's needs

IMPORTANT: You MUST respond with ONLY a valid JSON object in this exact format, nothing else:
{{
    "analysis": "Brief analysis of what the user is looking for",
    "recommendations": [
        {{
            "product_id": "id_from_list",
            "name": "product_name",
            "price": price_value,
            "url": "product_url",
            "reason": "Detailed explanation why this product matches the user's needs"
        }}
    ]
}}

Do not include any markdown formatting, code blocks, or additional text. Return only the JSON object.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from response (sometimes wrapped in markdown code blocks)
            if "```json" in response_text:
                # Extract JSON from markdown code block
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract from generic code block
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return raw text in a structured format
            return {
                "error": f"JSON parsing failed: {str(e)}",
                "analysis": "Could not parse AI response",
                "raw_response": response.text if 'response' in locals() else "No response"
            }
        except Exception as e:
            return {"error": str(e), "analysis": "Failed to generate recommendations"}

if __name__ == "__main__":
    # Example usage
    # Ensure GOOGLE_API_KEY is set in env
    finder = GeminiProductFinder()
    
    sample_products = [
        {"id": "1", "name": "Laptop Gaming ASUS", "price": 20000000, "features": "RTX 3050, i5 11400H"},
        {"id": "2", "name": "MacBook Air M1", "price": 18000000, "features": "M1 chip, lightweight"},
        {"id": "3", "name": "Laptop Dell Office", "price": 10000000, "features": "i3, basic tasks"},
    ]
    
    print(finder.find_products("Tôi cần mua laptop chơi game giá khoảng 20 triệu", sample_products))
