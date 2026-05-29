import os
import zlib
import struct

ASSETS = os.path.join(os.path.dirname(__file__), 'assets')
if not os.path.isdir(ASSETS):
    os.makedirs(ASSETS)

SIG = b'\x89PNG\r\n\x1a\n'

def png_chunk(tag, data):
    chunk = struct.pack('>I', len(data)) + tag + data
    crc = struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    return chunk + crc


def save_png(path, width, height, pixel_fn):
    raw = b''
    for y in range(height):
        row = b'\x00'
        for x in range(width):
            row += pixel_fn(x, y)
        raw += row
    compressed = zlib.compress(raw, level=9)
    with open(path, 'wb') as f:
        f.write(SIG)
        f.write(png_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)))
        f.write(png_chunk(b'IDAT', compressed))
        f.write(png_chunk(b'IEND', b''))


save_png(os.path.join(ASSETS, 'hero.png'), 64, 64, lambda x, y: (
    b'\x00\x00\x00\x00' if y < 8 or x < 8 or x >= 56 or y >= 56 else (
        b'\x74\x68\x32\xff' if 22 < x < 42 and 10 < y < 20 else
        b'\x34\x8b\xc8\xff' if 18 < x < 46 and 20 < y < 42 else
        b'\xad\x70\x2e\xff' if 20 < x < 44 and 42 < y < 56 else
        b'\x65\x43\x1e\xff' if 26 < x < 30 and 12 < y < 16 else
        b'\x65\x43\x1e\xff' if 34 < x < 38 and 12 < y < 16 else
        b'\x00\x00\x00\x00'
    )
))

save_png(os.path.join(ASSETS, 'enemy_robot.png'), 64, 64, lambda x, y: (
    b'\x00\x00\x00\x00' if y < 6 or y >= 58 or x < 6 or x >= 58 else (
        b'\x86\x8f\x99\xff' if 12 < x < 52 and 12 < y < 52 else
        b'\x2c\x2f\x34\xff' if 22 < x < 42 and 20 < y < 34 else
        b'\xff\x39\x39\xff' if 22 < x < 26 and 24 < y < 28 else
        b'\xff\x39\x39\xff' if 34 < x < 38 and 24 < y < 28 else
        b'\x36\x7d\x8b\xff' if 14 < x < 20 and 40 < y < 46 else
        b'\x36\x7d\x8b\xff' if 44 < x < 50 and 40 < y < 46 else
        b'\x6e\x6e\x6e\xff'
    )
))

save_png(os.path.join(ASSETS, 'enemy_monster.png'), 64, 64, lambda x, y: (
    b'\x00\x00\x00\x00' if y < 6 or y >= 58 or x < 6 or x >= 58 else (
        b'\x47\xb5\x2c\xff' if 10 < x < 54 and 10 < y < 54 else
        b'\x2f\x71\x1a\xff' if (x < 24 or x > 38) and y > 34 else
        b'\xff\xff\x00\xff' if 20 < x < 26 and 24 < y < 30 else
        b'\xff\xff\x00\xff' if 36 < x < 42 and 24 < y < 30 else
        b'\xff\x00\x00\xff' if 26 < x < 38 and 40 < y < 44 else
        b'\x2f\x71\x1a\xff'
    )
))

save_png(os.path.join(ASSETS, 'enemy_human.png'), 64, 64, lambda x, y: (
    b'\x00\x00\x00\x00' if y < 6 or y >= 60 or x < 6 or x >= 58 else (
        b'\x9b\x39\x32\xff' if 14 < x < 50 and 18 < y < 50 else
        b'\x56\x34\x12\xff' if 20 < x < 44 and 10 < y < 20 else
        b'\xfc\xe0\xa3\xff' if 24 < x < 40 and 20 < y < 34 else
        b'\x3c\x18\x0c\xff' if 22 < x < 42 and 34 < y < 44 else
        b'\x79\xbe\xf4\xff' if 18 < x < 46 and 44 < y < 54 else
        b'\x00\x00\x00\x00'
    )
))

save_png(os.path.join(ASSETS, 'weapon_blaster.png'), 36, 36, lambda x, y: (
    b'\x00\x00\x00\x00' if x < 4 or x >= 32 or y < 4 or y >= 32 else (
        b'\x53\xd0\xdc\xff' if 8 < x < 28 and 12 < y < 20 else
        b'\xff\xff\x82\xff' if 14 < x < 16 and 8 < y < 28 else
        b'\x1c\x4c\x65\xff'
    )
))

save_png(os.path.join(ASSETS, 'portal.png'), 60, 80, lambda x, y: (
    b'\x00\x00\x00\x00' if x < 6 or x >= 54 or y < 6 or y >= 74 else (
        b'\x6d\x3a\xa3\xff' if 16 < x < 44 and 10 < y < 70 else
        b'\xd4\x9b\xe4\xff' if 20 < x < 40 and 18 < y < 62 else
        b'\xff\xff\xff\xff' if 24 < x < 36 and 26 < y < 50 else
        b'\x8c\x2b\xa8\xff'
    )
))

print('Created placeholder assets in assets/')
