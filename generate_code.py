import json
import numpy as np
from typing import Dict, List, Any, Optional
from manim import *
from helper_functions import *

def main(json_file_path: str, output_file_path: str = "generated_scene.py") -> str:
    """
    Convert JSON geometric data to Manim scene code.
    Assumes all function calls have already been evaluated.
    """
    
    # Read JSON file
    with open(json_file_path, 'r') as f:
        scene_data = json.load(f)
    
    entities = {entity["id"]: entity for entity in scene_data["entities"]}
    positions = scene_data["positions"]
    relationships = scene_data.get("relationships", [])
    
    # Start building the Manim code
    code = '''from manim import *
import numpy as np
from helper_functions import *

class GeneratedScene(Scene):
    def construct(self):
'''
    
    entity_objects = {}
    
    # Create entities
    for entity_id, pos in positions.items():
        entity_info = entities[entity_id]
        entity_type = entity_info["type"]
        entity_color = entity_info.get("color", "WHITE")
        manim_color = entity_color
        
        if entity_type == "circle":
            center = pos["center"] if pos["center"] else [0, 0, 0]
            radius = float(pos["radius"]) if isinstance(pos["radius"], str) else pos["radius"]
            code += f"        {entity_id} = Circle(radius={radius}).move_to(np.array([{center[0]}, {center[1]}, 0]))\n"
            code += f"        {entity_id}.set_stroke(color={manim_color})\n"
            code += f"        {entity_id}.set_fill({manim_color}, opacity=0.3)\n"
            # Add center dot and label
            code += f"        {entity_id}_center_dot = Dot(point=np.array([{center[0]}, {center[1]}, 0]), color=WHITE)\n"
            code += f"        {entity_id}_center_label = Text('O', font_size=24).next_to({entity_id}_center_dot, RIGHT)\n"
            entity_objects[entity_id] = {"type": "circle", "manim_obj": f"{entity_id}"}
        
        elif entity_type == "semicircle":
            center = pos["center"] if pos["center"] else [0, 0, 0]
            radius = pos["radius"]
            orientation = entity_info.get("orientation", "up")
            
            # Set start angle and diameter endpoints based on orientation
            if orientation == "down":
                start_angle = np.pi
                diameter_start = [center[0] + radius, center[1], 0]
                diameter_end = [center[0] - radius, center[1], 0]
            elif orientation == "left":
                start_angle = np.pi/2
                diameter_start = [center[0], center[1] + radius, 0]
                diameter_end = [center[0], center[1] - radius, 0]
            elif orientation == "right":
                start_angle = -np.pi/2
                diameter_start = [center[0], center[1] + radius, 0]
                diameter_end = [center[0], center[1] - radius, 0]
            else:  # "up" or default
                start_angle = 0
                diameter_start = [center[0] + radius, center[1], 0]
                diameter_end = [center[0] - radius, center[1], 0]
            
            code += f"        # Create semicircle {entity_id}\n"
            code += f"        {entity_id}_arc = Arc(radius={radius}, start_angle={start_angle}, angle=np.pi, arc_center=np.array([{center[0]}, {center[1]}, 0]))\n"
            code += f"        {entity_id}_diameter = Line(\n"
            code += f"            np.array([{diameter_start[0]}, {diameter_start[1]}, {diameter_start[2]}]),\n"
            code += f"            np.array([{diameter_end[0]}, {diameter_end[1]}, {diameter_end[2]}])\n"
            code += f"        )\n"
            code += f"        {entity_id} = VGroup({entity_id}_arc, {entity_id}_diameter)\n"
            code += f"        {entity_id}.set_color({manim_color})\n"
            code += f"        {entity_id}.set_fill({manim_color}, opacity=0.3)\n"
            entity_objects[entity_id] = {"type": "semicircle", "manim_obj": f"{entity_id}"}
        
        elif entity_type == "square":
            vertices = pos["vertices"]
            code += f"        {entity_id} = Polygon(\n"
            for vertex in vertices:
                code += f"            np.array([{vertex[0]}, {vertex[1]}, {vertex[2]}]),\n"
            code = code.rstrip(',\n') + '\n'
            code += f"        )\n"
            code += f"        {entity_id}.set_stroke({manim_color}, width=2)\n"
            code += f"        {entity_id}.set_fill({manim_color}, opacity=0.3)\n"
            entity_objects[entity_id] = {"type": "square", "manim_obj": f"{entity_id}"}
        
        elif entity_type == "rectangle":
            vertices = pos["vertices"]
            code += f"        {entity_id} = Polygon(\n"
            for vertex in vertices:
                code += f"            np.array([{vertex[0]}, {vertex[1]}, {vertex[2]}]),\n"
            code = code.rstrip(',\n') + '\n'
            code += f"        )\n"
            code += f"        {entity_id}.set_stroke({manim_color}, width=2)\n"
            code += f"        {entity_id}.set_fill({manim_color}, opacity=0.3)\n"
            entity_objects[entity_id] = {"type": "rectangle", "manim_obj": f"{entity_id}"}
        
        elif entity_type == "triangle":
            vertices = pos["vertices"]
            code += f"        {entity_id} = Polygon(\n"
            for vertex in vertices:
                code += f"            np.array([{vertex[0]}, {vertex[1]}, {vertex[2]}]),\n"
            code = code.rstrip(',\n') + '\n'
            code += f"        )\n"
            code += f"        {entity_id}.set_stroke({manim_color}, width=2)\n"
            code += f"        {entity_id}.set_fill({manim_color}, opacity=0.3)\n"

        
        elif entity_type == "point":
            coords = pos["coordinates"]
            if isinstance(coords, str):
                # If it's a function call, evaluate it
                code += f"        {entity_id}_coords = {coords}\n"
                code += f"        if {entity_id}_coords is None:\n"
                code += f"            {entity_id}_coords = [0, 0, 0]  # Default coordinates if function returns None\n"
                code += f"        {entity_id} = Dot(point=np.array({entity_id}_coords), color={manim_color})\n"
            else:
                code += f"        {entity_id} = Dot(point=np.array([{coords[0]}, {coords[1]}, {coords[2]}]), color={manim_color})\n"
            # Add label for point
            code += f"        {entity_id}_label = Text('{entity_id}', font_size=24).next_to({entity_id}, RIGHT)\n"
            entity_objects[entity_id] = {"type": "point", "manim_obj": f"{entity_id}"}
        
        elif entity_type == "line":
            endpoints = pos["endpoints"]
            if isinstance(endpoints, str):
                # If endpoints is a function call string
                code += f"        {entity_id}_endpoints = {endpoints}\n"
                code += f"        if {entity_id}_endpoints is None:\n"
                code += f"            {entity_id}_endpoints = [[0, 0, 0], [1, 0, 0]]  # Default endpoints if function returns None\n"
                code += f"        {entity_id} = Line(np.array({entity_id}_endpoints[0]), np.array({entity_id}_endpoints[1]))\n"
            else:
                # Handle each endpoint which might be a function call or coordinates
                if isinstance(endpoints[0], str):
                    code += f"        {entity_id}_start = {endpoints[0]}\n"
                    code += f"        if {entity_id}_start is None:\n"
                    code += f"            {entity_id}_start = [0, 0, 0]  # Default start point if function returns None\n"
                    start_ref = f"{entity_id}_start"
                else:
                    start_point = endpoints[0]
                    start_ref = f"[{start_point[0]}, {start_point[1]}, {start_point[2]}]"
                
                if isinstance(endpoints[1], str):
                    code += f"        {entity_id}_end = {endpoints[1]}\n"
                    code += f"        if {entity_id}_end is None:\n"
                    code += f"            {entity_id}_end = [1, 0, 0]  # Default end point if function returns None\n"
                    end_ref = f"{entity_id}_end"
                else:
                    end_point = endpoints[1]
                    end_ref = f"[{end_point[0]}, {end_point[1]}, {end_point[2]}]"
                
                code += f"        {entity_id} = Line(np.array({start_ref}), np.array({end_ref}))\n"
            
            code += f"        {entity_id}.set_stroke(color={manim_color})\n"
            entity_objects[entity_id] = {"type": "line", "manim_obj": f"{entity_id}"}
        
        elif entity_type == "polygon":
            vertices = pos["vertices"]
            code += f"        {entity_id} = Polygon(\n"
            for vertex in vertices:
                code += f"            np.array([{vertex[0]}, {vertex[1]}, {vertex[2]}]),\n"
            code = code.rstrip(',\n') + '\n'
            code += f"        )\n"
            code += f"        {entity_id}.set_stroke({manim_color}, width=2)\n"
            code += f"        {entity_id}.set_fill({manim_color}, opacity=0.3)\n"
            entity_objects[entity_id] = {"type": "polygon", "manim_obj": f"{entity_id}"}
    
    # Add all objects to the scene
    code += "\n        # Add all objects to the scene\n"
    for entity_id in entity_objects:
        code += f"        self.add({entity_id})\n"
        if entity_objects[entity_id]["type"] == "circle":
            code += f"        self.add({entity_id}_center_dot, {entity_id}_center_label)\n"
        elif entity_objects[entity_id]["type"] == "point":
            code += f"        self.add({entity_id}_label)\n"
    
    code += '''
# To render: manim generated_scene.py GeneratedScene -pql
'''
    
    # Write to output file
    with open(output_file_path, 'w') as f:
        f.write(code)
    
    print(f"Manim code generated successfully in {output_file_path}")
    print(f"To render: manim {output_file_path} GeneratedScene -pql")
    
    return code

if __name__ == "__main__":    
    main("current_scene_final.json")