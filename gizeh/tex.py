import os
import hashlib
import tempfile
from pathlib import Path
from .gizeh import Element
from xml.dom import minidom
import re
from itertools import chain
import numpy as np

TEMPLATE_TEXT_BODY = r"""
\documentclass[preview]{{standalone}}

\usepackage[english]{{babel}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{dsfont}}
\usepackage{{setspace}}
\usepackage{{tipa}}
\usepackage{{relsize}}
\usepackage{{textcomp}}
\usepackage{{mathrsfs}}
\usepackage{{calligra}}
\usepackage{{wasysym}}
\usepackage{{ragged2e}}
\usepackage{{physics}}
\usepackage{{xcolor}}
\usepackage{{textcomp}}
\usepackage{{microtype}}
\DisableLigatures{{encoding = *, family = * }}
\linespread{{1}}

\begin{{document}}
{}
\end{{document}}"""


def tex_hash(expression):
    id_str = str(expression)
    hasher = hashlib.sha256()
    hasher.update(id_str.encode())
    # Truncating at 16 bytes for cleanliness
    return hasher.hexdigest()[:16]


def tex_to_svg(expression):
#    tmpdir = tempfile.TemporaryDirectory()
    tmpdir = Path.home().joinpath(".cache/gztex")
    tex_file = os.path.join(tmpdir, tex_hash(expression)) + ".tex"
    if not os.path.exists(tex_file):
        print("Writing \"%s\" to %s" % (
            "".join(expression), tex_file
        ))

        new_body = TEMPLATE_TEXT_BODY.format(expression)

        with open(tex_file, "w", encoding="utf-8") as outfile:
            outfile.write(new_body)

    dvi_file = tex_file.replace(".tex", ".dvi")
    if not os.path.exists(dvi_file):
        commands = ["latex", "-interaction=batchmode", "-halt-on-error",
                    "-output-directory=" + str(tmpdir), tex_file, ">", os.devnull]
        exit_code = os.system(" ".join(commands))
        if exit_code != 0:
            log_file = tex_file.replace(".tex", ".log")

            fd = open(log_file, 'r')
            lines = fd.readlines()
            for l in lines:
                print(l)

            raise Exception(
                ("Latex error converting to dvi. "
                 + "See log output above or the log file: %s" % log_file))

    svg_file = dvi_file.replace(".dvi", ".svg")
    if not os.path.exists(svg_file):
        commands = ["dvisvgm", dvi_file, "-n", "-v", "0",
                    "-o", svg_file, ">", os.devnull]
        os.system(" ".join(commands))
    with open(svg_file, "r") as f:
        svg_string = f.read()
    return svg_string


def string_to_numbers(num_string):
    num_string = num_string.replace("-", ",-")
    num_string = num_string.replace("e,-", "e-")
    return [float(s) for s in re.split("[ ,]", num_string) if s != ""]


class SVGElement(Element):

    def __init__(self, inputSVG):
        self.matrix = 1.0 * np.eye(3)
        self.svg_string = inputSVG
        self.fill = (0.0, 0.0, 0.0, 1.0)

    def handle_command(self, ctx, xy, command, coord_string):
        isLower = command.islower()
        command = command.upper()
        numbers = np.array(string_to_numbers(coord_string))
        xy = np.array(xy, dtype=float)

        if command == "M":  # moveto
            new_points = np.array(numbers).reshape((-1, 2))
            new_points += xy

            if isLower:
                new_points[0] += ctx.get_current_point()
                ctx.move_to(*new_points[0])
                for lp in new_points[1:]:
                    ctx.rel_line_to(*lp)
            else:
                ctx.move_to(*new_points[0])
                for lp in new_points[1:]:
                    ctx.line_to(*lp)

            return

        elif command in ["L", "H", "V"]:  # lineto

            p0 = ctx.get_current_point()
            if command == "H":
                new_points = np.zeros((len(numbers), 2))
                new_points[:, 0] = numbers + xy[0]
                if not isLower:
                    new_points[:, 1] = p0[1]

            elif command == "V":
                new_points = np.zeros((len(numbers), 2))
                if not isLower:
                    new_points[:, 0] = p0[0]
                new_points[:, 1] = numbers + xy[1]

            elif command == "L":
                new_points = numbers.reshape((-1, 2))
                new_points += xy

            for lp in new_points:
                if isLower:
                    ctx.rel_line_to(*lp)
                else:
                    ctx.line_to(*lp)
            return

        elif command == "C":  # curveto
            new_points = numbers.reshape(-1, 2)
            new_points += xy
            p0 = ctx.get_current_point()
            for i in range(0, len(new_points), 3):
                if isLower:
                    new_points[i:i + 3] += p0
                ctx.curve_to(*np.ravel(new_points[i:i + 3]))
                p0 = new_points[i + 2]
                self.last_control_point = 2*p0 - new_points[i + 1]

        elif command in ["S", "T"]:  # smooth curveto
            new_points = numbers.reshape((-1, 2))
            new_points += xy
            p0 = np.array(ctx.get_current_point())
            if isLower:
                new_points += p0
            new_points = np.vstack((self.last_control_point,
                                    new_points))
            self.last_control_point = 2*new_points[-1] - new_points[1]
            ctx.curve_to(*np.ravel(new_points))
        elif command in ("Q", "A"):
            raise RuntimeError("Not implemented")
        elif command == "Z":
            ctx.close_path()
        return

    def render_path(self, ctx, xy, path_string):
        pattern = "[MLHVCSQTAZmlhvcsqtaz]"
        pairs = list(zip(
            re.findall(pattern, path_string),
            re.split(pattern, path_string)[1:]
        ))
        for command, coord_string in pairs:
            self.handle_command(ctx, xy, command, coord_string)
        return ctx

    def get_objects_from(self, ctx, element, xy=[0, 0]):
        if not isinstance(element, minidom.Element):
            return []
        if element.tagName == 'defs':
            self.objects.update([
                (el.getAttribute('id'), el)
                for el in element.childNodes
                if isinstance(el, minidom.Element) and el.hasAttribute('id')
            ])
            return []
        elif element.tagName in ['g', 'svg']:
            return chain(*[self.get_objects_from(ctx, child)
                           for child in element.childNodes])
        elif element.tagName == 'path':
            path_string = element.getAttribute('d')
            self.render_path(ctx, xy, path_string)
            return []
        elif element.tagName == 'use':
            ref = element.getAttribute("xlink:href")[1:]
            x = element.getAttribute("x")
            y = element.getAttribute("y")
            return self.get_objects_from(ctx, self.objects[ref], xy=[x, y])
        elif element.tagName == 'rect':
            x, y, w, h = [float(element.getAttribute(j))
                          for j in ('x', 'y', 'width', 'height')]
            ctx.rectangle(x,y,w,h)
        elif element.tagName == 'circle':
            raise RuntimeError("circle")
        elif element.tagName == 'ellipse':
            raise RuntimeError("ellipse")
        elif element.tagName in ['polygon', 'polyline']:
            raise RuntimeError("poly")
        else:
            # print("I don't understand: ", element.tagName)
            pass


    def draw_method(self, ctx):
        self.objects = {}
        doc = minidom.parseString(self.svg_string)
        for svg in doc.getElementsByTagName("svg"):
            self.get_objects_from(ctx, svg)
        doc.unlink()
        ctx.set_source_rgba(*self.fill)
        ctx.fill_preserve()
