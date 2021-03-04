import gizeh
import moviepy.editor as mpy
import numpy as np

W,H = 128,128 # width, height, in pixels
duration = 6 # duration of the clip, in seconds

def make_frame(t):
    surface = gizeh.Surface(W,H)
    radius = W*(10+ (t*(duration-t))**2 )/200
    circle = gizeh.circle(radius, xy = (W/2,H/2), fill=((np.cos(3*t)+1.0)/2.0,0.0, 1.0))
    circle.draw(surface)
    return surface.get_npimage()

clip = mpy.VideoClip(make_frame, duration=duration)
print(dir(clip))
clip.write_videofile("circle.mp4",fps=15)
