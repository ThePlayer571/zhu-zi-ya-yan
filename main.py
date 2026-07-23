from manim import *


class Beautiful(Scene):
    def construct(self):
        title = Text("Hello, Manim!", font_size=72)

        self.play(Write(title))
        self.wait()

        self.play(title.animate.set_color(BLUE).scale(1.5))

        circle = Circle(color=YELLOW)
        self.play(ReplacementTransform(title, circle))

        self.play(circle.animate.rotate(PI))

        self.wait()