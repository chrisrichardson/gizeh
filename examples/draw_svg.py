import gizeh as gz
import moviepy.editor as mpy
import numpy as np
from PIL import Image

W, H = 1200, 800

# with open("Isaac_Newton_signature.svg", "r") as f:
with open("Robert_Hooke_signature.svg", "r") as f:
    svg = f.read()
s = gz.SVGElement(svg)

im = Image.open("paper_background2.jpg").resize((W, H))
im = np.array(im)

def make_frame1(t):
    surface = gz.Surface.from_image(im) # (W, H, bg_color=(1, 1, 1))

    p = s.translate((250, 250)).scale(0.1*t+1.0)
    p.fill = (0.0,0.0,0.0, t*t)
    p.draw(surface)

    return surface.get_npimage()


clip = mpy.VideoClip(make_frame1, duration=1.0)
# clip = mpy.concatenate_videoclips([clip1, clip2])
clip.write_videofile("draw_svg.mp4", fps=25)
