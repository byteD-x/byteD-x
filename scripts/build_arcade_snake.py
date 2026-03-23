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
.arcade-meter-track{fill:#201815;stroke:#ff9f1c;stroke-width:2;shape-rendering:crispEdges}
.arcade-footer{fill:#161616;stroke:#ff9f1c;stroke-width:2;shape-rendering:crispEdges}
.arcade-badge-pixel{fill:#f3efe6;stroke:#111111;stroke-width:2;shape-rendering:crispEdges}
.arcade-badge-auto{fill:#ffb347;stroke:#111111;stroke-width:2;shape-rendering:crispEdges}
.arcade-badge-live{fill:#72df67;stroke:#111111;stroke-width:2;shape-rendering:crispEdges}
.arcade-badge-text{fill:#111111;font-family:'Courier New',Consolas,monospace;font-size:7px;font-weight:700;letter-spacing:0.5px;text-anchor:middle}
.arcade-title{fill:#fff7e6;font-family:'Courier New',Consolas,monospace;font-size:12px;font-weight:700;letter-spacing:1px}
.arcade-footer-title{fill:#fff7e6;font-family:'Courier New',Consolas,monospace;font-size:9px;font-weight:700;letter-spacing:0.8px}
.arcade-footer-copy{fill:#d8c8aa;font-family:'Courier New',Consolas,monospace;font-size:7.5px;font-weight:700;letter-spacing:0.4px}
.arcade-legend-text{fill:#f3efe6;font-family:'Courier New',Consolas,monospace;font-size:7px;font-weight:700;letter-spacing:0.35px}
.arcade-legend-idle{fill:#f3efe6;stroke:#111111;stroke-width:2;shape-rendering:crispEdges}
.arcade-legend-low{fill:#b7f77a;stroke:#111111;stroke-width:2;shape-rendering:crispEdges}
.arcade-legend-mid{fill:#5bbe4a;stroke:#111111;stroke-width:2;shape-rendering:crispEdges}
.arcade-legend-hot{fill:#ff9f1c;stroke:#111111;stroke-width:2;shape-rendering:crispEdges}
.arcade-legend-peak{fill:#e5484d;stroke:#111111;stroke-width:2;shape-rendering:crispEdges}
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


def append_rect(parent: ET.Element, attrs: dict[str, str]) -> ET.Element:
    return ET.SubElement(parent, svg_tag("rect"), attrs)


def add_badge(parent: ET.Element, x: int, width: int, rect_class: str, label: str) -> None:
    append_rect(parent, {"class": rect_class, "x": str(x), "y": "-17", "width": str(width), "height": "11"})
    append_text(parent, "text", {"class": "arcade-badge-text", "x": str(x + (width / 2)), "y": "-9"}, label)


def add_legend_item(parent: ET.Element, swatch_class: str, x: int, label: str) -> None:
    append_rect(parent, {"class": swatch_class, "x": str(x), "y": "137", "width": "9", "height": "9"})
    append_text(parent, "text", {"class": "arcade-legend-text", "x": str(x + 15), "y": "144"}, label)


def build_arcade_frame() -> ET.Element:
    frame = ET.Element(svg_tag("g"), {"id": "arcade-frame"})

    append_rect(frame, {"class": "arcade-shell", "x": "-16", "y": "-32", "width": "880", "height": "192"})
    append_rect(frame, {"class": "arcade-shadow", "x": "-6", "y": "-20", "width": "860", "height": "164"})
    append_rect(frame, {"class": "arcade-bezel", "x": "-12", "y": "-28", "width": "872", "height": "180"})
    append_rect(frame, {"class": "arcade-topbar", "x": "-4", "y": "-20", "width": "856", "height": "20"})
    append_rect(frame, {"class": "arcade-screen", "x": "-4", "y": "-1", "width": "856", "height": "120"})
    append_rect(frame, {"class": "arcade-meter-track", "x": "0", "y": "115", "width": "848", "height": "8"})
    append_rect(frame, {"class": "arcade-footer", "x": "-4", "y": "130", "width": "856", "height": "24"})

    append_text(frame, "text", {"class": "arcade-title", "x": "14", "y": "-7"}, "BYTED-X // PIXEL ARCADE")
    add_badge(frame, 694, 46, "arcade-badge-pixel", "PIXEL")
    add_badge(frame, 746, 42, "arcade-badge-auto", "AUTO")
    add_badge(frame, 794, 42, "arcade-badge-live", "LIVE")

    append_text(frame, "text", {"class": "arcade-footer-title", "x": "14", "y": "141"}, "Contribution Snake")
    append_text(frame, "text", {"class": "arcade-footer-copy", "x": "14", "y": "149"}, "GitHub activity replayed as a pixel crawl // refresh every 12h")

    add_legend_item(frame, "arcade-legend-idle", 588, "Idle")
    add_legend_item(frame, "arcade-legend-low", 637, "Low")
    add_legend_item(frame, "arcade-legend-mid", 684, "Mid")
    add_legend_item(frame, "arcade-legend-hot", 731, "Hot")
    add_legend_item(frame, "arcade-legend-peak", 778, "Peak")

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

        if "u" in classes:
            rect.set("y", "115")
            rect.set("height", "8")

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
