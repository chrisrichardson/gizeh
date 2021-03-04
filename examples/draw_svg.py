import gizeh as gz
import moviepy.editor as mpy
import numpy as np
from PIL import Image

W, H = 1200, 800

# with open("Isaac_Newton_signature.svg", "r") as f:
with open("Robert_Hooke_Signature.svg", "r") as f:
    svg = f.read()
s = gz.SVGElement(svg)

im = Image.open("paper_background2.jpg").resize((W, H))
im = np.array(im)

def make_arrow(x0, y0, x1, y1, **kw):

    # parameters
    w = 0.01
    hw = 0.1
    hl = 0.2

    a = np.array([x0, y0])
    b = np.array([x1, y1])
    n = (b - a)
    t = np.array((-n[1], n[0]))
    pts = np.array([a + w*t, b + w*t, b + hw*t, b + hl*n,
                    b - hw*t, b - w*t, a - w*t])

    return gz.polyline(pts, close_path=True, **kw)

def make_frame1(t):
    surface = gz.Surface.from_image(im) # (W, H, bg_color=(1, 1, 1))

    arr = make_arrow(30,30,100,100, fill=(0,0,0))
    arr.draw(surface)

    p = s.translate((250, 250)).scale(0.1*t+1.0)
    p.fill = (0.0,0.0,0.0, t*t)
    p.draw(surface)

    return surface.get_npimage()


# clip = mpy.VideoClip(make_frame1, duration=1.0)
# clip = mpy.concatenate_videoclips([clip1, clip2])
#clip.write_videofile("draw_svg.mp4", fps=25)

im = make_frame1(0.0)
im = Image.fromarray(im)
im.show()
