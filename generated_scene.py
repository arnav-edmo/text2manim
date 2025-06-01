from manim import *
import numpy as np
from helper_functions import *

class GeneratedScene(Scene):
    def construct(self):
        C1 = Circle(radius=3).move_to(np.array([0, 0, 0]))
        C1.set_stroke(color=GREEN)
        C1.set_fill(GREEN, opacity=0.3)
        C1_center_dot = Dot(point=np.array([0, 0, 0]), color=WHITE)
        C1_center_label = Text('O', font_size=24).next_to(C1_center_dot, RIGHT)
        S1 = Polygon(
            np.array([-2.1215, -2.1215, 0.0]),
            np.array([2.1215, -2.1215, 0.0]),
            np.array([2.1215, 2.1215, 0.0]),
            np.array([-2.1215, 2.1215, 0.0])
        )
        S1.set_stroke(BLUE, width=2)
        S1.set_fill(BLUE, opacity=0.3)
        P1 = Dot(point=np.array([5.83, 0, 0]), color=ORANGE)
        P1_label = Text('P1', font_size=24).next_to(P1, RIGHT)
        # Create line T1
        T1_start = np.array([1.543739279588336, -2.5723275523649947, 0.0])
        T1_end = np.array([5.83, 0.0, 0.0])
        T1 = Line(T1_start, T1_end)
        T1.set_stroke(color=RED)
        # Create line T2
        T2_start = np.array([1.543739279588336, 2.5723275523649947, 0.0])
        T2_end = np.array([5.83, 0.0, 0.0])
        T2 = Line(T2_start, T2_end)
        T2.set_stroke(color=RED)

        # Add all objects to the scene
        self.add(C1)
        self.add(C1_center_dot, C1_center_label)
        self.add(S1)
        self.add(P1)
        self.add(P1_label)
        self.add(T1)
        self.add(T2)

# To render: manim generated_scene.py GeneratedScene -pql
