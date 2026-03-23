#!/usr/bin/env python3
from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
NS_TAG = f"{{{SVG_NS}}}"

ET.register_namespace("", SVG_NS)

STYLE_APPEND = """
.arcade-shell{fill:#0b0b0b}
.arcade-shadow{fill:#24130a;shape-rendering:crispEdges}
.arcade-bezel{fill:#141414;stroke:#ff7a00;stroke-width:4;shape-rendering:crispEdges}
.arcade-topbar{fill:#241712}
.arcade-screen{fill:#f3efe6;stroke:#161616;stroke-width:4;shape-rendering:crispEdges}
.arcade-footer{fill:#161616;stroke:#ff9f1c;stroke-width:2;shape-rendering:crispEdges}
.arcade-led-green{fill:#5bbe4a;shape-rendering:crispEdges}
.arcade-led-orange{fill:#ff9f1c;shape-rendering:crispEdges}
.arcade-led-red{fill:#e5484d;shape-rendering:crispEdges}
.arcade-chip{fill:#111111;font-family:'Courier New',Consolas,monospace;font-size:9px;font-weight:700;letter-spacing:1.2px}
.arcade-title{fill:#fff7e6;font-family:'Courier New',Consolas,monospace;font-size:12px;font-weight:700;letter-spacing:1.6px}
.arcade-status{fill:#f8efe0;font-family:'Courier New',Consolas,monospace;font-size:10px;font-weight:700;letter-spacing:1.3px}
.arcade-subtle{fill:#d8c8aa;font-family:'Courier New',Consolas,monospace;font-size:9px;font-weight:700;letter-spacing:1px}
""".strip()

ROOT_REPLACEMENTS = {
    "--cb:#1b1f230a;": "--cb:#d8d2c4;",
    "--cs:purple;": "--cs:#111111;",
    "--ce:#ebedf0;": "--ce:#f3efe6;",
    "--c0:#ebedf0;": "--c0:#f3efe6;",
    "--c1:#9be9a8;": "--c1:#b7f77a;",
    "--c2:#40c463;": "--c2:#5bbe4a;",
    "--c3:#30a14e;": "--c3:#ff9f1c;",
    "--c4:#216e39": "--c4:#e5484d",
    "shape-rendering:geometricPrecision": "shape-rendering:crispEdges",
}

SNAKE_LAYER_GEOMETRY = {
    "s0": {"x": "0", "y": "0", "width": "16", "height": "16"},
    "s1": {"x": "1", "y": "1", "width": "14", "height": "14"},
    "s2": {"x": "3", "y": "3", "width": "10", "height": "10"},
    "s3": {"x": "4", "y": "4", "width": "8", "height": "8"},
}


def svg_tag(name: str) -> str:
    return f"{NS_TAG}{name}"


def append_text(parent: ET.Element, tag: str, attrs: dict[str, str], text: str) -> ET.Element:
    element = ET.SubElement(parent, svg_tag(tag), attrs)
    element.text = text
    return element


def build_arcade_frame() -> ET.Element:
    frame = ET.Element(svg_tag("g"), {"id": "arcade-frame"})

    ET.SubElement(frame, svg_tag("rect"), {"class": "arcade-shell", "x": "-16", "y": "-32", "width": "880", "height": "192"})
    ET.SubElement(frame, svg_tag("rect"), {"class": "arcade-shadow", "x": "-6", "y": "-20", "width": "860", "height": "164"})
    ET.SubElement(frame, svg_tag("rect"), {"class": "arcade-bezel", "x": "-12", "y": "-28", "width": "872", "height": "180"})
    ET.SubElement(frame, svg_tag("rect"), {"class": "arcade-topbar", "x": "-4", "y": "-20", "width": "856", "height": "18"})
    ET.SubElement(frame, svg_tag("rect"), {"class": "arcade-screen", "x": "-4", "y": "-2", "width": "856", "height": "116"})
    ET.SubElement(frame, svg_tag("rect"), {"class": "arcade-footer", "x": "-4", "y": "132", "width": "856", "height": "24"})

    ET.SubElement(frame, svg_tag("rect"), {"class": "arcade-led-orange", "x": "730", "y": "-16", "width": "18", "height": "10"})
    ET.SubElement(frame, svg_tag("rect"), {"class": "arcade-led-red", "x": "754", "y": "-16", "width": "18", "height": "10"})
    ET.SubElement(frame, svg_tag("rect"), {"class": "arcade-led-green", "x": "778", "y": "-16", "width": "18", "height": "10"})

    append_text(frame, "text", {"class": "arcade-title", "x": "14", "y": "-7"}, "BYTED-X // PIXEL ARCADE")
    append_text(frame, "text", {"class": "arcade-chip", "x": "734", "y": "-8"}, "1UP")
    append_text(frame, "text", {"class": "arcade-chip", "x": "758", "y": "-8"}, "RUN")
    append_text(frame, "text", {"class": "arcade-chip", "x": "782", "y": "-8"}, "LIVE")
    append_text(frame, "text", {"class": "arcade-status", "x": "14", "y": "148"}, "CONTRIBUTION SNAKE // AUTO REFRESH 12H")
    append_text(frame, "text", {"class": "arcade-subtle", "x": "650", "y": "148"}, "BLK WHT GRN ORG RED")

    return frame


def transform_style(style: ET.Element) -> None:
    if not style.text:
        raise ValueError("SVG style block is missing.")

    style_text = style.text
    for old, new in ROOT_REPLACEMENTS.items():
        style_text = style_text.replace(old, new)

    style_text = style_text.replace(
        ".u{transform-origin:0 0;transform:scale(0,1);animation:none linear 21100ms infinite}",
        ".u{shape-rendering:crispEdges;transform-origin:0 0;transform:scale(0,1);animation:none linear 21100ms infinite}",
    )
    style.text = f"{style_text}\n{STYLE_APPEND}"


def pixelate_rectangles(root: ET.Element) -> None:
    for rect in root.iter(svg_tag("rect")):
        classes = rect.attrib.get("class", "").split()
        if not classes:
            continue

        if "c" in classes or "u" in classes:
            rect.attrib.pop("rx", None)
            rect.attrib.pop("ry", None)

        snake_layers = [name for name in classes if name in SNAKE_LAYER_GEOMETRY]
        if snake_layers:
            rect.attrib.pop("rx", None)
            rect.attrib.pop("ry", None)
            for key, value in SNAKE_LAYER_GEOMETRY[snake_layers[0]].items():
                rect.set(key, value)


def transform_svg(input_path: Path, output_path: Path) -> None:
    tree = ET.parse(input_path)
    root = tree.getroot()

    style = root.find(svg_tag("style"))
    if style is None:
        raise ValueError("SVG style tag not found.")

    transform_style(style)
    pixelate_rectangles(root)

    insert_index = 0
    for index, child in enumerate(list(root)):
        if child.tag == svg_tag("style"):
            insert_index = index + 1
            break

    root.insert(insert_index, build_arcade_frame())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a snk SVG into a pixel arcade themed snake.")
    parser.add_argument("input_svg", type=Path)
    parser.add_argument("output_svg", type=Path)
    args = parser.parse_args()

    transform_svg(args.input_svg, args.output_svg)


if __name__ == "__main__":
    main()
