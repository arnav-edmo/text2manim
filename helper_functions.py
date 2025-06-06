from manim import *
import numpy as np
from typing import List, Tuple, Optional

def get_tangent_by_point(circle_center, circle_radius, external_point) -> Tuple[List[float], List[float]]:
    """Calculate tangent points on circle from external point.
    Returns both tangent points and the external point as pairs forming two tangent lines.
    """
    O = np.array(circle_center, dtype=float)
    P = np.array(external_point, dtype=float)
    OP = P[:2] - O[:2]
    d = np.linalg.norm(OP)
    
    if d <= circle_radius:
        return None
    
    # Calculate angle between OP and tangent
    theta = np.arccos(circle_radius / d)
    phi = np.arctan2(OP[1], OP[0])
    
    # Calculate both tangent points
    angle1 = phi + theta
    angle2 = phi - theta
    
    T1_xy = O[:2] + circle_radius * np.array([np.cos(angle1), np.sin(angle1)])
    T2_xy = O[:2] + circle_radius * np.array([np.cos(angle2), np.sin(angle2)])
    
    T1 = [T1_xy[0], T1_xy[1], O[2] if len(O) > 2 else 0]
    T2 = [T2_xy[0], T2_xy[1], O[2] if len(O) > 2 else 0]
    P_3d = [P[0], P[1], O[2] if len(O) > 2 else 0]
    
    return [T1, P_3d], [T2, P_3d]

def get_tangent_by_angle_between_tangents(circle_center, circle_radius, angle) -> Tuple[List[float], List[float]]:
    """Calculate tangent points on circle given angle between tangents.
    Angle is in radians. Returns two pairs of points forming the tangent lines.
    """
    O = np.array(circle_center, dtype=float)
    
    # Calculate distance to external point using angle
    # From the formula: sin(angle/2) = radius/distance
    distance = circle_radius / np.sin(angle/2)
    
    # Place external point to the right of circle center
    P = [O[0] + distance, O[1], O[2] if len(O) > 2 else 0]
    
    # Use get_tangent_by_point to find the tangent points
    return get_tangent_by_point(circle_center, circle_radius, P)

def get_tangent_by_angle_with_radius(circle_center, circle_radius, angle) -> Tuple[List[float], List[float]]:
    """Calculates tangent if the angle between the tangent and line joining the center of the circle to the point of tangency is given.
    """
    return get_tangent_by_angle_between_tangents(circle_center, circle_radius, angle*2)[0]

def get_tangent_by_distance_from_center(circle_center, circle_radius, distance_from_center) -> Tuple[List[float], List[float]]:
    """Calculate tangent lines from a originating from a point given its distance from the center.
    
    Args:
        circle_center: [x, y, z] coordinates of circle center
        circle_radius: radius of circle
        distance_from_center: distance from circle center to point where tangent originates
    
    Returns:
        Tuple of two points representing the tangent points on the circle
    """
    if distance_from_center <= circle_radius:
        return None
    
    # Calculate angle between radius and tangent using trigonometry
    theta = np.arccos(circle_radius / distance_from_center)
    
    # Place point at specified distance along positive x-axis
    P = [circle_center[0] + distance_from_center, circle_center[1], circle_center[2] if len(circle_center) > 2 else 0]
    
    # Use get_tangent_by_point to find tangent points
    return get_tangent_by_point(circle_center, circle_radius, P)

def get_tangent_by_length_of_tangent(circle_center, circle_radius, length_of_tangent) -> Tuple[List[float], List[float]]:
    """Calculate tangent points given length of tangent.
    
    Args:
        circle_center: [x, y, z] coordinates of circle center
        circle_radius: radius of circle
        length_of_tangent: length of the tangent line from external point to circle
    
    Returns:
        Tuple of two points representing the tangent points on the circle
    """
    # Using Pythagorean theorem: tangent^2 = distance^2 - radius^2
    # Solve for distance from center to external point
    distance_from_center = np.sqrt(length_of_tangent**2 + circle_radius**2)
    
    # Use get_tangent_by_distance_from_center to find tangent points
    return get_tangent_by_distance_from_center(circle_center, circle_radius, distance_from_center)

def get_chord_from_center_distance(circle_center: List[float], circle_radius: float, distance_from_center: float) -> Tuple[List[float], List[float]]:
    """Calculate endpoints of a chord given its distance from center."""
    if abs(distance_from_center) >= circle_radius:
        return None
    
    half_length = np.sqrt(circle_radius**2 - distance_from_center**2)
    x1 = -half_length
    x2 = half_length
    y = distance_from_center
    
    # Rotate to standard position
    points = []
    for x in [x1, x2]:
        points.append([
            circle_center[0] + x,
            circle_center[1] + y,
            circle_center[2] if len(circle_center) > 2 else 0
        ])
    
    return points[0], points[1]

def get_chord_from_length(circle_center: List[float], circle_radius: float, chord_length: float) -> Tuple[List[float], List[float]]:
    """Calculate endpoints of a chord given its length."""
    if chord_length > 2 * circle_radius:
        return None
    
    half_length = chord_length / 2
    distance_from_center = np.sqrt(circle_radius**2 - half_length**2)
    return get_chord_from_center_distance(circle_center, circle_radius, distance_from_center)

def get_common_chord(circle1_center: List[float], circle1_radius: float, circle2_center: List[float], circle2_radius: float) -> Tuple[List[float], List[float]]:
    """Calculate endpoints of the common chord between two intersecting circles.
    
    Args:
        circle1_center: [x, y, z] coordinates of first circle
        circle1_radius: radius of first circle
        circle2_center: [x, y, z] coordinates of second circle
        circle2_radius: radius of second circle
    
    Returns:
        Tuple of two points representing the endpoints of common chord, or None if circles don't intersect
    """
    # Convert centers to numpy arrays for easier calculation
    O1 = np.array(circle1_center)
    O2 = np.array(circle2_center)
    
    # Calculate distance between centers
    d = np.linalg.norm(O2[:2] - O1[:2])  # Only use x,y coordinates
    
    # Check if circles intersect
    if d > circle1_radius + circle2_radius:  # Too far apart
        return None
    if d < abs(circle1_radius - circle2_radius):  # One inside other
        return None
    
    # Calculate distance from center1 to radical axis
    # Using the radical axis theorem
    a = (circle1_radius**2 - circle2_radius**2 + d**2)/(2*d)
    
    # Calculate height of chord using Pythagorean theorem
    h = np.sqrt(circle1_radius**2 - a**2)
    
    # Calculate unit vector from O1 to O2
    unit_d = (O2[:2] - O1[:2])/d
    
    # Calculate perpendicular unit vector
    unit_perp = np.array([-unit_d[1], unit_d[0]])
    
    # Calculate center point of common chord
    chord_center = O1[:2] + a*unit_d
    
    # Calculate endpoints
    endpoint1 = np.append(chord_center + h*unit_perp, O1[2] if len(O1) > 2 else 0)
    endpoint2 = np.append(chord_center - h*unit_perp, O1[2] if len(O1) > 2 else 0)
    
    return list(endpoint1), list(endpoint2)

def get_inscribed_circle(vertices: List[List[float]]) -> Tuple[List[float], float]:
    """Calculate center and radius of inscribed circle in a triangle."""
    if len(vertices) != 3:
        return None
    
    # Calculate side lengths
    a = np.sqrt((vertices[1][0] - vertices[2][0])**2 + (vertices[1][1] - vertices[2][1])**2)
    b = np.sqrt((vertices[0][0] - vertices[2][0])**2 + (vertices[0][1] - vertices[2][1])**2)
    c = np.sqrt((vertices[0][0] - vertices[1][0])**2 + (vertices[0][1] - vertices[1][1])**2)
    
    # Calculate semi-perimeter
    s = (a + b + c) / 2
    
    # Calculate radius
    radius = np.sqrt((s - a)*(s - b)*(s - c)/s)
    
    # Calculate center
    center = [
        (a*vertices[0][0] + b*vertices[1][0] + c*vertices[2][0])/(a + b + c),
        (a*vertices[0][1] + b*vertices[1][1] + c*vertices[2][1])/(a + b + c),
        vertices[0][2] if len(vertices[0]) > 2 else 0
    ]
    
    return center, radius

def get_circumscribed_circle(vertices: List[List[float]]) -> Tuple[List[float], float]:
    """Calculate center and radius of circumscribed circle around a triangle."""
    if len(vertices) != 3:
        return None
    
    # Calculate side lengths
    a = np.sqrt((vertices[1][0] - vertices[2][0])**2 + (vertices[1][1] - vertices[2][1])**2)
    b = np.sqrt((vertices[0][0] - vertices[2][0])**2 + (vertices[0][1] - vertices[2][1])**2)
    c = np.sqrt((vertices[0][0] - vertices[1][0])**2 + (vertices[0][1] - vertices[1][1])**2)
    
    # Calculate semi-perimeter
    s = (a + b + c) / 2
    
    # Calculate area
    area = np.sqrt(s*(s-a)*(s-b)*(s-c))
    
    # Calculate radius
    radius = (a*b*c)/(4*area)
    
    # Calculate center
    D = 2*(vertices[0][0]*(vertices[1][1] - vertices[2][1]) + 
           vertices[1][0]*(vertices[2][1] - vertices[0][1]) + 
           vertices[2][0]*(vertices[0][1] - vertices[1][1]))
    
    center = [
        ((vertices[0][0]**2 + vertices[0][1]**2)*(vertices[1][1] - vertices[2][1]) +
         (vertices[1][0]**2 + vertices[1][1]**2)*(vertices[2][1] - vertices[0][1]) +
         (vertices[2][0]**2 + vertices[2][1]**2)*(vertices[0][1] - vertices[1][1]))/D,
        ((vertices[0][0]**2 + vertices[0][1]**2)*(vertices[2][0] - vertices[1][0]) +
         (vertices[1][0]**2 + vertices[1][1]**2)*(vertices[0][0] - vertices[2][0]) +
         (vertices[2][0]**2 + vertices[2][1]**2)*(vertices[1][0] - vertices[0][0]))/D,
        vertices[0][2] if len(vertices[0]) > 2 else 0
    ]
    
    return center, radius

def get_square_vertices(center: List[float], side_length: float, orientation: float = 0) -> List[List[float]]:
    """Calculate vertices of a square given center, side length, and orientation (in radians)."""
    half_side = side_length / 2
    vertices = [
        [-half_side, -half_side],
        [half_side, -half_side],
        [half_side, half_side],
        [-half_side, half_side]
    ]
    
    # Rotate vertices
    cos_theta = np.cos(orientation)
    sin_theta = np.sin(orientation)
    rotated_vertices = []
    for vertex in vertices:
        x_rot = vertex[0]*cos_theta - vertex[1]*sin_theta + center[0]
        y_rot = vertex[0]*sin_theta + vertex[1]*cos_theta + center[1]
        rotated_vertices.append([x_rot, y_rot, center[2] if len(center) > 2 else 0])
    
    return rotated_vertices

def get_rectangle_vertices(center: List[float], length: float, width: float, orientation: float = 0) -> List[List[float]]:
    """Calculate vertices of a rectangle given center, dimensions, and orientation (in radians)."""
    half_length = length / 2
    half_width = width / 2
    vertices = [
        [-half_length, -half_width],
        [half_length, -half_width],
        [half_length, half_width],
        [-half_length, half_width]
    ]
    
    # Rotate vertices
    cos_theta = np.cos(orientation)
    sin_theta = np.sin(orientation)
    rotated_vertices = []
    for vertex in vertices:
        x_rot = vertex[0]*cos_theta - vertex[1]*sin_theta + center[0]
        y_rot = vertex[0]*sin_theta + vertex[1]*cos_theta + center[1]
        rotated_vertices.append([x_rot, y_rot, center[2] if len(center) > 2 else 0])
    
    return rotated_vertices

def get_equilateral_triangle_vertices(center: List[float], side_length: float, orientation: float = 0) -> List[List[float]]:
    """Calculate vertices of an equilateral triangle given center, side length, and orientation (in radians)."""
    # Height of equilateral triangle
    height = side_length * np.sqrt(3) / 2
    
    # Base vertices before rotation and translation
    vertices = [
        [-side_length/2, -height/3],  # Bottom left
        [side_length/2, -height/3],   # Bottom right
        [0, 2*height/3]               # Top
    ]
    
    # Rotate and translate vertices
    cos_theta = np.cos(orientation)
    sin_theta = np.sin(orientation)
    rotated_vertices = []
    for vertex in vertices:
        x_rot = vertex[0]*cos_theta - vertex[1]*sin_theta + center[0]
        y_rot = vertex[0]*sin_theta + vertex[1]*cos_theta + center[1]
        rotated_vertices.append([x_rot, y_rot, center[2] if len(center) > 2 else 0])
    
    return rotated_vertices

def get_isosceles_triangle_vertices(center: List[float], equal_sides: float, base: float, orientation: float = 0) -> List[List[float]]:
    """Calculate vertices of an isosceles triangle given center, equal sides length, base length, and orientation."""
    # Height using Pythagorean theorem
    if equal_sides <= base/2:
        raise ValueError("Equal sides must be longer than half the base")
    height = np.sqrt(equal_sides**2 - (base/2)**2)
    
    # Base vertices before rotation and translation
    vertices = [
        [-base/2, -height/3],    # Bottom left
        [base/2, -height/3],     # Bottom right
        [0, 2*height/3]          # Top
    ]
    
    # Rotate and translate vertices
    cos_theta = np.cos(orientation)
    sin_theta = np.sin(orientation)
    rotated_vertices = []
    for vertex in vertices:
        x_rot = vertex[0]*cos_theta - vertex[1]*sin_theta + center[0]
        y_rot = vertex[0]*sin_theta + vertex[1]*cos_theta + center[1]
        rotated_vertices.append([x_rot, y_rot, center[2] if len(center) > 2 else 0])
    
    return rotated_vertices

def get_right_triangle_vertices(center: List[float], base: float, height: float, orientation: float = 0) -> List[List[float]]:
    """Calculate vertices of a right triangle given center, base, height, and orientation."""
    # Base vertices before rotation and translation (right angle at origin)
    vertices = [
        [-base/3, -height/3],     # Bottom left
        [2*base/3, -height/3],    # Bottom right
        [-base/3, 2*height/3]     # Top
    ]
    
    # Rotate and translate vertices
    cos_theta = np.cos(orientation)
    sin_theta = np.sin(orientation)
    rotated_vertices = []
    for vertex in vertices:
        x_rot = vertex[0]*cos_theta - vertex[1]*sin_theta + center[0]
        y_rot = vertex[0]*sin_theta + vertex[1]*cos_theta + center[1]
        rotated_vertices.append([x_rot, y_rot, center[2] if len(center) > 2 else 0])
    
    return rotated_vertices

def get_scalene_triangle_vertices(center: List[float], sides: List[float], orientation: float = 0) -> List[List[float]]:
    """Calculate vertices of a scalene triangle given center and three sides using law of cosines."""
    a, b, c = sides
    
    # Check if triangle is possible
    if (a + b <= c) or (b + c <= a) or (a + c <= b):
        raise ValueError("Triangle inequality violated: sum of any two sides must be greater than the third side")
    
    # Calculate angles using law of cosines
    cos_A = (b**2 + c**2 - a**2) / (2*b*c)
    angle_A = np.arccos(np.clip(cos_A, -1.0, 1.0))
    
    # Calculate vertices in local coordinates
    vertices = [
        [0, 0],                     # First vertex at origin
        [c, 0],                     # Second vertex along x-axis
        [b*np.cos(angle_A), b*np.sin(angle_A)]  # Third vertex
    ]
    
    # Center the triangle
    centroid = [sum(v[0] for v in vertices)/3, sum(v[1] for v in vertices)/3]
    centered_vertices = [[v[0]-centroid[0], v[1]-centroid[1]] for v in vertices]
    
    # Rotate and translate vertices
    cos_theta = np.cos(orientation)
    sin_theta = np.sin(orientation)
    rotated_vertices = []
    for vertex in centered_vertices:
        x_rot = vertex[0]*cos_theta - vertex[1]*sin_theta + center[0]
        y_rot = vertex[0]*sin_theta + vertex[1]*cos_theta + center[1]
        rotated_vertices.append([x_rot, y_rot, center[2] if len(center) > 2 else 0])
    
    return rotated_vertices

def get_triangle_vertices_from_angles_side(center: List[float], side: float, angles: List[float], orientation: float = 0) -> List[List[float]]:
    """Calculate vertices of a triangle given one side length and two angles."""
    if len(angles) != 2:
        raise ValueError("Must provide exactly two angles")
    
    # Calculate third angle
    third_angle = np.pi - sum(angles)
    if third_angle <= 0:
        raise ValueError("Sum of angles must be less than 180 degrees")
    
    # Calculate other sides using law of sines
    side_b = side * np.sin(angles[0]) / np.sin(third_angle)
    side_c = side * np.sin(angles[1]) / np.sin(third_angle)
    
    # Use scalene triangle function to get vertices
    return get_scalene_triangle_vertices(center, [side, side_b, side_c], orientation)

def get_triangle_type(sides: Optional[List[float]] = None, angles: Optional[List[float]] = None) -> str:
    """Determine the type of triangle based on sides and/or angles."""
    if sides and len(sides) == 3:
        # Check if equilateral
        if abs(sides[0] - sides[1]) < 1e-6 and abs(sides[1] - sides[2]) < 1e-6:
            return "equilateral"
        # Check if isosceles
        elif abs(sides[0] - sides[1]) < 1e-6 or abs(sides[1] - sides[2]) < 1e-6 or abs(sides[0] - sides[2]) < 1e-6:
            return "isosceles"
    
    if angles and len(angles) == 3:
        # Check if right triangle
        if any(abs(angle - np.pi/2) < 1e-6 for angle in angles):
            return "right"
        # Check if equilateral
        if all(abs(angle - np.pi/3) < 1e-6 for angle in angles):
            return "equilateral"
    
    if sides and len(sides) == 3:
        # If not any special case, it's scalene
        return "scalene"
    
    return "unknown"