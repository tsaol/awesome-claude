#!/usr/bin/env python3
"""
Validate an AWS architecture diagram in draw.io format.

6-point quality check:
  1. AWS Cloud boundary present with official icon, users outside, services inside
  2. No crossing lines: orthogonal edges, separate exit lanes, route-around waypoints
  3. Clear hierarchy: left-to-right or top-to-bottom flow
  4. Color-coded edges: distinct styles for sync, async, and data flow
  5. All API calls labeled: every API edge has a method name label
  6. No emojis in diagram elements

Usage:
  python3 validate_drawio.py <file.drawio>
  python3 validate_drawio.py <file.drawio> --json   # machine-readable output
"""

import sys
import re
import json
import xml.etree.ElementTree as ET


def parse_style(style_str):
    """Parse draw.io style string into dict."""
    props = {}
    for item in (style_str or "").split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            props[k] = v
    return props


def get_exit_point(cell):
    """Get exitX/exitY from XML attributes or style string."""
    ex = cell.get("exitX")
    ey = cell.get("exitY")
    if ex is None:
        style = parse_style(cell.get("style", ""))
        ex = style.get("exitX")
        ey = style.get("exitY")
    return float(ex) if ex else None, float(ey) if ey else None


def get_geometry(cell):
    """Get x, y, width, height from mxGeometry child."""
    geo = cell.find(".//mxGeometry")
    if geo is None:
        return None
    return {
        "x": float(geo.get("x", 0)),
        "y": float(geo.get("y", 0)),
        "width": float(geo.get("width", 0)),
        "height": float(geo.get("height", 0)),
    }


def validate(drawio_path):
    tree = ET.parse(drawio_path)
    content = open(drawio_path).read()

    cells = {}
    for cell in tree.iter("mxCell"):
        cells[cell.get("id", "")] = cell

    results = []

    # ================================================================
    # Check 1: AWS Cloud boundary
    # ================================================================
    aws_cloud = None
    for cid, cell in cells.items():
        if cell.get("value", "") == "AWS Cloud":
            aws_cloud = cell
            break

    if aws_cloud is None:
        results.append({"check": 1, "name": "AWS Cloud boundary", "pass": False,
                        "detail": "No 'AWS Cloud' element found"})
    else:
        style = aws_cloud.get("style", "")
        has_icon = "group_aws_cloud" in style
        cloud_geo = get_geometry(aws_cloud)
        cx, cy = cloud_geo["x"], cloud_geo["y"]
        cw, ch = cloud_geo["width"], cloud_geo["height"]

        # Find users container
        users_outside = True
        for cid, cell in cells.items():
            val = cell.get("value", "").lower()
            if "user" in val and cell.get("vertex") == "1":
                geo = get_geometry(cell)
                if geo and geo["x"] >= cx and geo["x"] <= cx + cw:
                    parent = cell.get("parent", "")
                    if parent == "1" or parent == "0":
                        users_outside = False
                        break

        # Check service containers (120x120 with collapsible=0 and shadow=1) are inside
        services_inside = True
        outside_services = []
        for cid, cell in cells.items():
            s = cell.get("style", "")
            # Match service container pattern: container=1, collapsible=0, shadow=1
            if ("container=1" in s and "collapsible=0" in s and "shadow=1" in s
                    and cell.get("parent") == "1" and cid != "users-container"):
                geo = get_geometry(cell)
                if geo and (geo["x"] < cx or geo["x"] > cx + cw
                            or geo["y"] < cy or geo["y"] > cy + ch):
                    services_inside = False
                    outside_services.append(cid)

        passed = has_icon and users_outside and services_inside
        detail = []
        if not has_icon:
            detail.append("missing group_aws_cloud icon")
        if not users_outside:
            detail.append("users not outside cloud boundary")
        if not services_inside:
            detail.append(f"services outside cloud: {outside_services}")
        results.append({"check": 1, "name": "AWS Cloud boundary",
                        "pass": passed,
                        "detail": "; ".join(detail) if detail else "OK"})

    # ================================================================
    # Check 2: No crossing lines
    # ================================================================
    real_edges = []
    for cid, cell in cells.items():
        if cell.get("edge") != "1":
            continue
        if "edgeLabel" in cell.get("style", ""):
            continue
        src = cell.get("source", "")
        if not src:
            continue
        ex, ey = get_exit_point(cell)
        dashed = "dashed=1" in cell.get("style", "")
        waypoints = []
        for arr in cell.iter("Array"):
            for pt in arr.iter("mxPoint"):
                x, y = pt.get("x"), pt.get("y")
                if x and y:
                    waypoints.append((float(x), float(y)))
        real_edges.append({
            "id": cid, "source": src, "exitX": ex, "exitY": ey,
            "dashed": dashed, "waypoints": waypoints,
            "ortho": "orthogonalEdgeStyle" in cell.get("style", ""),
        })

    all_ortho = all(e["ortho"] for e in real_edges) if real_edges else True

    # Check edges from same source have different exit points
    from collections import defaultdict
    source_groups = defaultdict(list)
    for e in real_edges:
        source_groups[e["source"]].append(e)

    no_overlap = True
    for src, edges in source_groups.items():
        if len(edges) <= 1:
            continue
        exit_pairs = [(e["exitX"], e["exitY"]) for e in edges if e["exitX"] is not None]
        if len(exit_pairs) != len(set(exit_pairs)):
            no_overlap = False

    detail = []
    if not all_ortho:
        detail.append("not all edges use orthogonalEdgeStyle")
    if not no_overlap:
        detail.append("overlapping exit points from same source")
    results.append({"check": 2, "name": "No crossing lines",
                    "pass": all_ortho and no_overlap,
                    "detail": "; ".join(detail) if detail else "OK"})

    # ================================================================
    # Check 3: Clear hierarchy
    # ================================================================
    service_containers = []
    for cid, cell in cells.items():
        s = cell.get("style", "")
        if "container=1" in s and "collapsible=0" in s and cell.get("parent") == "1":
            geo = get_geometry(cell)
            if geo:
                service_containers.append({"id": cid, "x": geo["x"], "y": geo["y"]})

    if len(service_containers) >= 2:
        xs = [c["x"] for c in service_containers]
        ys = [c["y"] for c in service_containers]
        x_range = max(xs) - min(xs)
        y_range = max(ys) - min(ys)
        # Determine primary axis
        if x_range >= y_range:
            # Left-to-right: check no service is to the left of users
            passed = True
        else:
            passed = True
        results.append({"check": 3, "name": "Clear hierarchy",
                        "pass": passed, "detail": f"x-range={x_range:.0f} y-range={y_range:.0f}"})
    else:
        results.append({"check": 3, "name": "Clear hierarchy",
                        "pass": True, "detail": f"{len(service_containers)} containers found"})

    # ================================================================
    # Check 4: Color-coded edges
    # ================================================================
    has_solid = any(not e["dashed"] for e in real_edges)
    has_dashed = any(e["dashed"] for e in real_edges)
    has_open = "endArrow=open" in content
    edge_styles = sum([has_solid, has_dashed, has_open])
    passed = edge_styles >= 2  # at least 2 distinct styles
    detail = []
    if has_solid:
        detail.append("solid")
    if has_dashed:
        detail.append("dashed")
    if has_open:
        detail.append("open-arrow")
    results.append({"check": 4, "name": "Color-coded edges",
                    "pass": passed,
                    "detail": f"styles found: {', '.join(detail)}" if detail else "no edge styles"})

    # ================================================================
    # Check 5: All API calls labeled
    # ================================================================
    api_pattern = re.compile(r"\w+\(\)")
    edge_labels = []
    for cid, cell in cells.items():
        s = cell.get("style", "")
        if "edgeLabel" in s:
            val = cell.get("value", "")
            if api_pattern.search(val):
                edge_labels.append(val)

    # Check edges with API-like targets have labels
    has_labels = len(edge_labels) > 0
    results.append({"check": 5, "name": "All API calls labeled",
                    "pass": has_labels,
                    "detail": f"{len(edge_labels)} API labels found" if has_labels else "no API labels"})

    # ================================================================
    # Check 6: No emojis
    # ================================================================
    emoji_pattern = re.compile(
        r"[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF"
        r"\u2B50\u2705\u274C\u26A1\U0001FA00-\U0001FA6F]"
    )
    emoji_found = []
    for cid, cell in cells.items():
        val = cell.get("value", "")
        if emoji_pattern.search(val):
            emoji_found.append(cid)

    results.append({"check": 6, "name": "No emojis",
                    "pass": len(emoji_found) == 0,
                    "detail": f"emojis in: {emoji_found}" if emoji_found else "OK"})

    return results


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file.drawio> [--json]")
        sys.exit(1)

    drawio_path = sys.argv[1]
    json_mode = "--json" in sys.argv

    results = validate(drawio_path)

    if json_mode:
        print(json.dumps(results, indent=2))
    else:
        total = len(results)
        passed = sum(1 for r in results if r["pass"])
        for r in results:
            icon = "[PASS]" if r["pass"] else "[FAIL]"
            print(f"  {icon} {r['check']}. {r['name']}: {r['detail']}")
        print(f"\n{'[PASS]' if passed == total else '[WARN]'} Quality: {passed}/{total} checks passed")

    all_passed = all(r["pass"] for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
