import json
import numpy as np
from typing import Dict, Any, List
from helper_functions import *

def parse_array_literal(array_str: str) -> List[float]:
    """Parse an array literal string into a list of floats."""
    try:
        # Remove any whitespace and ensure it's a valid array literal
        clean_str = array_str.strip()
        if not (clean_str.startswith('[') and clean_str.endswith(']')):
            return None
        
        # Parse the array string
        array_str = clean_str[1:-1]  # Remove brackets
        if not array_str.strip():
            return []
        
        # Split by comma and convert to floats
        values = [float(x.strip()) for x in array_str.split(',')]
        return values
    except:
        return None

def evaluate_function_call(value: str) -> Any:
    """Evaluate a function call string."""
    try:
        # Extract function name and parameters
        func_name = value[:value.find("(")]
        params_str = value[value.find("(")+1:value.rfind(")")]
        
        # Parse parameters
        params = []
        current_param = ""
        bracket_count = 0
        
        for char in params_str:
            if char == ',' and bracket_count == 0:
                if current_param.strip():
                    params.append(current_param.strip())
                current_param = ""
            else:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                current_param += char
        
        if current_param.strip():
            params.append(current_param.strip())
        
        # Convert parameters to appropriate types
        converted_params = []
        for param in params:
            param = param.strip()
            if param.startswith("[") and param.endswith("]"):
                # Parse array parameter
                array_result = parse_array_literal(param)
                if array_result is not None:
                    converted_params.append(array_result)
                else:
                    converted_params.append([])
            elif param.startswith("'") or param.startswith('"'):
                # Parse string parameter
                param_value = param.strip("'\"")
                # Map 'upper' to 'right' and 'lower' to 'left' for get_single_tangent_point
                if func_name == "get_single_tangent_point":
                    side_map = {'upper': 'right', 'lower': 'left'}
                    param_value = side_map.get(param_value, param_value)
                converted_params.append(param_value)
            elif param.lower() == "true":
                converted_params.append(True)
            elif param.lower() == "false":
                converted_params.append(False)
            elif param.lower() == "null" or param.lower() == "none":
                converted_params.append(None)
            else:
                try:
                    # Try to convert to float first
                    converted_params.append(float(param))
                except ValueError:
                    # If that fails, keep as string
                    converted_params.append(param)
        
        # Call the appropriate function
        func = globals()[func_name]
        result = func(*converted_params)
        
        # Convert result to list if it's numpy array
        if isinstance(result, np.ndarray):
            result = result.tolist()
        elif isinstance(result, tuple):
            result = [r.tolist() if isinstance(r, np.ndarray) else r for r in result]
        
        return result
    except Exception as e:
        print(f"Error evaluating function {value}: {str(e)}")
        return None

def evaluate_value(value: Any) -> Any:
    """Evaluate a value that might be a function call or array literal."""
    if not isinstance(value, str):
        return value
        
    # First try to parse as array literal
    if value.strip().startswith('[') and value.strip().endswith(']'):
        array_result = parse_array_literal(value)
        if array_result is not None:
            return array_result
        
    # Then try to evaluate as function call
    if any(fname in value for fname in [
        "get_single_tangent_point",
        "get_chord_points",
        "get_square_vertices",
        "get_rectangle_vertices",
        "get_equilateral_triangle_vertices",
        "get_right_triangle_vertices",
        "get_isosceles_triangle_vertices",
        "get_scalene_triangle_vertices",
    ]):
        result = evaluate_function_call(value)
        if result is not None:
            return result
        
    return value

def evaluate_function_calls(json_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate function calls in the JSON schema."""
    positions = json_schema.get("positions", {})
    evaluated_positions = {}
    
    for entity_id, position_data in positions.items():
        evaluated_position = {}
        for key, value in position_data.items():
            if isinstance(value, list):
                # Handle arrays of values
                evaluated_position[key] = [evaluate_value(item) for item in value]
            else:
                # Handle single values
                evaluated_position[key] = evaluate_value(value)
        evaluated_positions[entity_id] = evaluated_position
    
    json_schema["positions"] = evaluated_positions
    return json_schema

def main():
    try:
        # Read the input JSON file
        with open('current_scene.json', 'r') as f:
            json_schema = json.load(f)

        # Process the positions using the functional approach
        processed_schema = evaluate_function_calls(json_schema)

        # Write the processed JSON to the output file
        with open('current_scene_final.json', 'w') as f:
            json.dump(processed_schema, f, indent=2)
        
        print("Successfully processed positions and saved to current_scene_final.json")
    except FileNotFoundError:
        print("Error: current_scene.json not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in current_scene.json")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()