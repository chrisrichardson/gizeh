import gizeh as gz
import moviepy.editor as mpy
import numpy as np
from PIL import Image

W, H = 600, 480

# with open("Isaac_Newton_signature.svg", "r") as f:
with open("Robert_Hooke_Signature.svg", "r") as f:
    svg = f.read()
s = gz.SVGElement(svg)

im = Image.open("paper_background2.jpg").resize((W, H))
im = np.array(im)

def make_arrow(x0, x1, w=0.01, hw=0.05, hl=0.1, **kw):

    a = np.array(x0)
    b = np.array(x1)
    n = (b - a)
    t = np.array((-n[1], n[0]))
    pts = np.array([a + w*t, b + w*t - hl*n, b + hw*t - hl*n, b,
                    b - hw*t - hl*n, b - w*t - hl*n, a - w*t])

    return gz.polyline(pts, close_path=True, **kw)

def make_frame1(t):
    surface = gz.Surface.from_image(im) # (W, H, bg_color=(1, 1, 1))

    b = 200
    th = 0.0
    for i in range(20):
        x0 = [b + b * np.cos(th), b + b * np.sin(th)]
        th += 2.0*np.pi/20
        x1 = [b + b * np.cos(th), b + b * np.sin(th)]
        arr = make_arrow(x0, x1, hl=0.25, fill=(0,0,0), stroke_width=0)
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
