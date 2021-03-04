import gizeh as gz
import moviepy.editor as mpy
import numpy as np
from PIL import Image

H = 450
W = (H * 16)//9
# W, H = 1600, 900

# with open("Isaac_Newton_signature.svg", "r") as f:
with open("Robert_Hooke_Signature.svg", "r") as f:
    svg = f.read()
s = gz.SVGElement(svg)

im = Image.open("paper_background2.jpg").resize((W, H))
im = np.array(im)

def make_frame1(t):
    surface = gz.Surface.from_image(im)
    w = surface.width
    h = surface.height

    b = 200
    th = 0.0

    # Graph axes
    arr = gz.arrow((0.1*w, 0.9*h),(0.1*w, 0.1*h), fill=(0,0,0))
    arr.draw(surface)
    arr = gz.arrow((0.05*w, 0.85*h),(0.95*w, 0.85*h), fill=(0,0,0))
    arr.draw(surface)

    pts = []
    for i in range(int(1500*t) + 1):
        x = 0.1*w+i*w/5000
        pts += [[x, 50*np.cos(x/1.5)+100*np.cos(x/1.4)+200]]
    pl = gz.polyline(pts, stroke_width=2.0)
    pl.draw(surface)

    return surface.get_npimage()


clip = mpy.VideoClip(make_frame1, duration=3.0)
# clip = mpy.concatenate_videoclips([clip1, clip2])
clip.write_videofile("draw_svg.mp4", fps=25)

# im = make_frame1(0.0)
# im = Image.fromarray(im)
# im.show()
