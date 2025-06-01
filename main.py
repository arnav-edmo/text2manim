import json
import re
import os
from dotenv import load_dotenv
import requests
from typing import Dict, Any

load_dotenv()

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

def get_few_shot_examples(description: str) -> str:
    """Get few shot examples for the description."""

    few_shot_examples = ""

    description = description.lower()

    if "circle" in description:
        with open('few_shot_examples/circle.txt', 'r') as f:
            few_shot_examples += f.read()

    if "square" in description:
        with open('few_shot_examples/square.txt', 'r') as f:
            few_shot_examples += f.read()

    if "rectangle" in description:
        with open('few_shot_examples/rectangle.txt', 'r') as f:
            few_shot_examples += f.read()

    if "triangle" in description:
        with open('few_shot_examples/triangle.txt', 'r') as f:
            few_shot_examples += f.read()

    if "tangent" in description:
        with open('few_shot_examples/tangent.txt', 'r') as f:
            few_shot_examples += f.read()

    if "inscribe" in description:
        with open('few_shot_examples/inscribe.txt', 'r') as f:
            few_shot_examples += f.read()

    if "circumscribe" in description:
        with open('few_shot_examples/circumscribe.txt', 'r') as f:
            few_shot_examples += f.read()

    if "chord" in description:
        with open('few_shot_examples/chord.txt', 'r') as f:
            few_shot_examples += f.read()

    if "semi" in description:
        with open('few_shot_examples/semicircle.txt', 'r') as f:
            few_shot_examples += f.read()

    return few_shot_examples

def generate_json_schema(description: str, model_name: str = "llama-3.1-8b-instant") -> Dict[str, Any]:
    """Generate a JSON schema for the geometric description using Chain of Thought."""
    # Get API configuration
    config = get_api_config(model_name)
    
    # Sanitize input
    truncated_description = re.sub(r'[{}]', '', description).replace('\n', ' ').strip()

    few_shot_examples = get_few_shot_examples(description)

    prompt = """You are a geometric parser with expert knowledge of geometric principles. Use Chain of Thought to analyze the geometric problem and convert it into a JSON schema.
    Your task is to extract all information about the image from the question. You are NOT required to SOLVE the question.

    CRITICAL RULES FOR JSON STRUCTURE:
    1. All numeric values must be plain numbers (e.g., 5 not "5")
    2. All coordinates must be arrays of numbers (e.g., [0, 0, 0] not "[0, 0, 0]")
    3. Function calls must be strings (e.g., "get_square_vertices([0, 0, 0], 5, 0)")
    4. Do not add any explanatory text after the JSON
    5. The JSON must be valid and complete
    6. Do NOT use BLACK color for any shape
    7. For derived calculations:
        - Square inscribed in circle: side = radius * sqrt(2)
        - Circle inscribed in square: radius = side / 2
        - Semicircle on line: center = midpoint of line, radius = line_length / 2
    8. All entity IDs must be unique

    NEVER put geometric properties (radius, side_length, etc.) only in entities - they MUST be in positions section for manim code generation.

    AVAILABLE GEOMETRIC FUNCTIONS:
    1. get_single_tangent_point(circle_center, circle_radius, external_point, side)
    2. get_square_vertices(center, side_length, orientation)
    3. get_rectangle_vertices(center, length, width, orientation)
    4. get_equilateral_triangle_vertices(center, side_length, orientation)
    5. get_isosceles_triangle_vertices(center, equal_sides, base, orientation)
    6. get_right_triangle_vertices(center, base, height, orientation)
    7. get_chord_points(circle_center, circle_radius, distance_from_center)
    8. get_inscribed_circle(vertices)
    9. get_circumscribed_circle(vertices)

    """ + few_shot_examples + """

    Now, analyze this input and generate a JSON schema for: """ + truncated_description + """
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
        with open('current_scene.json', 'w') as f:
            json.dump(json_schema, f, indent=2)
        print(json.dumps(json_schema, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()