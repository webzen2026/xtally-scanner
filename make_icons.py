#!/usr/bin/env python3
"""Generate PWA icon set for Xtally Scanner — a scan-frame (viewfinder
corners) around a small document mark on an amber->orange gradient
rounded-square, distinct from Xtally Documents (indigo/fuchsia) and
Xtally Sheets (teal/emerald)."""
from PIL import Image, ImageDraw

# Brand colors
C1 = (245, 158, 11)   # amber-500
C2 = (234, 88, 12)    # orange-600
WHITE = (255, 255, 255, 255)


def gradient_square(size, radius_ratio=0.22):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = grad.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)  # diagonal gradient
            r = int(C1[0] + (C2[0] - C1[0]) * t)
            g = int(C1[1] + (C2[1] - C1[1]) * t)
            b = int(C1[2] + (C2[2] - C1[2]) * t)
            px[x, y] = (r, g, b, 255)
    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    radius = int(size * radius_ratio)
    mdraw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    img.paste(grad, (0, 0), mask)
    return img


def draw_scan_mark(img, scale=1.0, offset=(0, 0)):
    """Draw four viewfinder/scan-frame corner brackets around a small
    centered document rectangle with a scan-line — centered on the
    canvas, sized by `scale` (1.0 = content fills ~62% of canvas, safe
    for maskable icons)."""
    size = img.width
    draw = ImageDraw.Draw(img)

    content = size * 0.62 * scale
    cx, cy = size / 2 + offset[0], size / 2 + offset[1]
    left = cx - content / 2
    top = cy - content / 2
    right = left + content
    bottom = top + content

    stroke_w = max(2, content * 0.07)
    bracket = content * 0.30

    # Four L-shaped viewfinder corner brackets
    for (bx, by, dx, dy) in [
        (left, top, 1, 1), (right, top, -1, 1),
        (left, bottom, 1, -1), (right, bottom, -1, -1),
    ]:
        draw.line([bx, by, bx + bracket * dx, by], fill=WHITE, width=int(stroke_w))
        draw.line([bx, by, bx, by + bracket * dy], fill=WHITE, width=int(stroke_w))

    # Centered document card (slightly smaller, filled, with folded corner)
    doc_w = content * 0.40
    doc_h = content * 0.52
    dleft = cx - doc_w / 2
    dtop = cy - doc_h / 2
    dright = dleft + doc_w
    dbottom = dtop + doc_h
    fold = doc_w * 0.32

    draw.polygon([
        (dleft, dtop), (dright - fold, dtop), (dright, dtop + fold),
        (dright, dbottom), (dleft, dbottom),
    ], fill=WHITE)
    # folded-corner triangle in the accent color for depth
    mid_t = 0.5
    fold_color = (
        int(C1[0] + (C2[0] - C1[0]) * mid_t),
        int(C1[1] + (C2[1] - C1[1]) * mid_t),
        int(C1[2] + (C2[2] - C1[2]) * mid_t),
        255,
    )
    draw.polygon([(dright - fold, dtop), (dright, dtop + fold), (dright - fold, dtop + fold)], fill=fold_color)

    # scan-line across the document (a bright accent bar)
    scan_y = dtop + doc_h * 0.62
    draw.rectangle([dleft + doc_w * 0.12, scan_y - stroke_w * 0.35,
                     dright - doc_w * 0.12, scan_y + stroke_w * 0.35], fill=fold_color)

    return img


def make_icon(size, filename, maskable=False):
    img = gradient_square(size, radius_ratio=0.0 if maskable else 0.22)
    scale = 0.62 if maskable else 1.0
    draw_scan_mark(img, scale=scale)
    img.save(filename)
    print("wrote", filename, img.size)


if __name__ == "__main__":
    make_icon(512, "icons/icon-512.png")
    make_icon(192, "icons/icon-192.png")
    make_icon(512, "icons/icon-maskable-512.png", maskable=True)
    make_icon(180, "icons/apple-touch-icon.png")
    make_icon(32, "icons/favicon-32.png")
    make_icon(16, "icons/favicon-16.png")

    # og:image (1200x630) — gradient banner with mark + wordmark space
    og = Image.new("RGBA", (1200, 630), (0, 0, 0, 0))
    grad = gradient_square(1200, radius_ratio=0)
    og.paste(grad, (0, 0))
    og = og.crop((0, (1200 - 630) // 2, 1200, (1200 - 630) // 2 + 630))
    mark_canvas = Image.new("RGBA", (630, 630), (0, 0, 0, 0))
    draw_scan_mark(mark_canvas, scale=0.75, offset=(0, 0))
    og.paste(mark_canvas, (60, 0), mark_canvas)
    og.convert("RGB").save("icons/og-image.png", quality=92)
    print("wrote icons/og-image.png", og.size)
