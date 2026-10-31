#!/usr/bin/env python3
"""The icon of SensorCheck as the PNGs its Info.plist names (no asset catalog: actool is a Mac program): a radar
screen -- three rings and a cross, a sweep fading out behind its bright leading edge, two echoes in what it has
swept -- on a dark green to teal gradient. SpringBoard rounds the corners itself.
usage: python3 -I mkicon.py APP_DIR"""
import math
import os
import struct
import sys
import zlib

TOP, BOTTOM = (0x05, 0x2e, 0x1f), (0x0b, 0x80, 0x88)
SCREEN = (0x02, 0x1c, 0x16)                 # the radar's own disc, darker than the gradient
SWEEP = (0x5c, 0xff, 0xb0)
RING = (0xc8, 0xff, 0xe6)
SS = 4      # samples per pixel along each side

CX, CY, R = 0.5, 0.5, 0.40                  # the radar's centre and radius
EDGE = math.radians(52)                     # the sweep's leading edge, counter-clockwise from 3 o'clock
TRAIL = math.radians(100)                   # how far behind it the sweep fades to nothing (it turns clockwise)
ECHOES = ((0.58, math.radians(24), 0.030), (0.82, math.radians(66), 0.024))  # (radius / R, behind the edge, size)


def mix(c, d, a):
    return tuple(x + (y - x) * a for x, y in zip(c, d))


def color(u, v, bg):
    dx, dy = u - CX, CY - v                 # y up, as angles are measured
    r = math.hypot(dx, dy)
    if r > R + 0.02:
        return bg
    c = mix(bg, SCREEN, 0.55) if r <= R else bg

    if r <= R:
        # the sweep: brightest at the edge, fading over TRAIL behind it (behind = counter-clockwise of it)
        behind = (math.atan2(dy, dx) - EDGE) % (2 * math.pi)
        if behind < TRAIL:
            c = mix(c, SWEEP, 0.62 * (1 - behind / TRAIL) ** 1.6)
        # the rings at a third, two thirds and the rim, and the cross
        for ring, width in ((R / 3, 0.006), (2 * R / 3, 0.006)):
            if abs(r - ring) < width:
                c = mix(c, RING, 0.40)
        if abs(dx) < 0.005 or abs(dy) < 0.005:
            c = mix(c, RING, 0.30)
        # the leading edge itself
        ex, ey = math.cos(EDGE), math.sin(EDGE)
        if dx * ex + dy * ey > 0 and abs(dx * ey - dy * ex) < 0.009:
            c = mix(c, SWEEP, 0.95)
        # the echoes, each with a faint halo
        for er, ea, size in ECHOES:
            a = EDGE + ea
            d = math.hypot(dx - er * R * math.cos(a), dy - er * R * math.sin(a))
            if d < size:
                c = mix(c, (0xe8, 0xff, 0xf0), 0.95)
            elif d < size * 2:
                c = mix(c, SWEEP, 0.35 * (2 - d / size))
        if r < 0.018:
            c = mix(c, RING, 0.9)
    if abs(r - R) < 0.012:
        c = mix(c, RING, 0.75)
    return c


def png(size):
    rows = []
    for y in range(size):
        row = bytearray([0])
        bg = [a + (b - a) * y / (size - 1) for a, b in zip(TOP, BOTTOM)]
        for x in range(size):
            total = [0, 0, 0]
            for i in range(SS):
                for j in range(SS):
                    c = color((x + (i + 0.5) / SS) / size, (y + (j + 0.5) / SS) / size, bg)
                    total = [t + k for t, k in zip(total, c)]
            row += bytes(min(255, round(t / (SS * SS))) for t in total)
        rows.append(bytes(row))

    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(b''.join(rows), 9)) + chunk(b'IEND', b''))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for scale in (2, 3):
        with open(os.path.join(sys.argv[1], 'AppIcon60x60@%dx.png' % scale), 'wb') as f:
            f.write(png(60 * scale))


main()
