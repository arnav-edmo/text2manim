import json
import re
import os
import requests
from typing import Dict, Any

# Global cache for storing results
cache = {}

def get_api_config(model_name: str = "llama-3.1-8b-instant") -> Dict[str, str]:
    """Get API configuration including API key and URL."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    return {
        "model_name": model_name,
        "api_key": api_key,
        "api_url": "https://api.groq.com/openai/v1/chat/completions"
    }

def generate_json_schema(description: str, model_name: str = "llama-3.1-8b-instant") -> Dict[str, Any]:
    """Generate a JSON schema for the geometric description using Chain of Thought."""
    # Get API configuration
    config = get_api_config(model_name)
    
    # Sanitize input
    sanitized_description = re.sub(r'[{}]', '', description).replace('\n', ' ').strip()
    
    # Check cache
    global cache
    if sanitized_description in cache:
        return cache[sanitized_description]
    
    with open('json_prompt.txt', 'r') as f:
        json_prompt = f.read()

    prompt = """You are a geometric parser with expert knowledge of geometric principles. Use Chain of Thought to analyze the geometric problem and convert it into a JSON schema.
    Your task is to extract all information about the image from the question. You are NOT required to SOLVE the question.

    """ + json_prompt + """

    Now, analyze this input and generate a JSON schema for: """ + sanitized_description + """
    First provide your Chain of Thought analysis, then output the JSON schema starting with the line "JSON Output:" followed by the JSON on a new line. Do not add any explanatory text after the JSON."""

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": config["model_name"],
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 10000,
        "top_p": 0.9
    }

    try:
        response = requests.post(config["api_url"], headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            output = result["choices"][0]["message"]["content"].strip()
            
            # Extract JSON part
            json_marker = "JSON Output:"
            if json_marker not in output:
                raise ValueError("No JSON output marker found in response")
            
            # Split at JSON marker and take everything after it
            json_text = output.split(json_marker)[1].strip()
            
            # Print Chain of Thought analysis
            cot_analysis = output.split(json_marker)[0].strip()
            print("Chain of Thought Analysis:")
            print(cot_analysis)
            print("\nGenerated JSON Schema:")
            
            try:
                # Try to find the JSON object boundaries
                json_start = json_text.find('{')
                json_end = json_text.rfind('}') + 1
                if json_start == -1 or json_end <= json_start:
                    raise ValueError("No valid JSON object found in the text")
                
                clean_json = json_text[json_start:json_end]
                json_schema = json.loads(clean_json)
                
                # Cache the result
                cache[sanitized_description] = json_schema
                return json_schema
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {json_text}")
                raise ValueError(f"Invalid JSON format: {str(e)}")
        else:
            raise ValueError("Unexpected API response format")
            
    except Exception as e:
        raise ValueError(f"Failed to generate JSON schema: {str(e)}")

def main():
    """Main function to handle command line input and generate JSON schema."""
    with open('prompt.txt', 'r') as f:
        question = f.readline()
    
    print(f"\nProcessing question: {question}")
    try:
        json_schema = generate_json_schema(question)
        # Write the JSON to a file for code_gen.py to use
        with open('current_scene.json', 'w') as f:
            json.dump(json_schema, f, indent=2)
        print(json.dumps(json_schema, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()