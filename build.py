# usage: python3 -I build.py <dl dir> <out repo dir>
import sys, os, json, urllib.request
from PIL import Image, ImageFilter
DL, OUT = sys.argv[1], sys.argv[2]
ROLES = 'KQRBNP'
NAMES = dict(K='king', Q='queen', R='rook', B='bishop', N='knight', P='pawn')
pack = {'name': 'Modern Mix', 'pieces': [], 'board': []}

def save(img, path, size):
    """Pad to square (bottom-aligned, keeps relative piece scale) and upscale nearest-neighbour."""
    s = max(img.size); sq = Image.new('RGBA', (s, s))
    sq.paste(img, ((s - img.width) // 2, s - img.height))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sq.resize((size, size), Image.NEAREST).save(path)

def pieceset(name, folder, ext='png'):
    pack['pieces'].append({'name': name, 'path': f'pieces/{folder}/{{piece}}.{ext}'})

def outline(img, color=(30, 30, 40, 255)):
    """1px outline around opaque pixels (the source's white pieces have none)."""
    pad = Image.new('RGBA', (img.width + 2, img.height + 2)); pad.paste(img, (1, 1))
    ring = pad.getchannel('A').filter(ImageFilter.MaxFilter(3))
    out = Image.new('RGBA', pad.size, color); out.putalpha(ring)
    return Image.alpha_composite(out, pad)

def sheet(name, folder, file, cell, order, rows, size=128, box=None, fix=None):
    """rows: {'w': row_index, 'b': row_index}; order: roles left to right; fix: {'w': fn} per color."""
    im = Image.open(os.path.join(DL, file)).convert('RGBA')
    for color, r in rows.items():
        for i, role in enumerate(order):
            x, y = i * cell, r * cell
            crop = im.crop(box(color, i) if box else (x, y, x + cell, y + cell))
            if fix and color in fix: crop = fix[color](crop)
            save(crop, f'{OUT}/pieces/{folder}/{color}{role}.png', size)
    pieceset(name, folder)

def files(name, folder, pattern, size, smooth=False):
    for c, cn in (('w', 'white'), ('b', 'black')):
        for r in ROLES:
            im = Image.open(os.path.join(DL, pattern.format(color=cn, role=NAMES[r]))).convert('RGBA')
            if smooth:
                os.makedirs(f'{OUT}/pieces/{folder}', exist_ok=True)
                im.resize((size, size), Image.LANCZOS).save(f'{OUT}/pieces/{folder}/{c}{r}.png')
            else:
                save(im, f'{OUT}/pieces/{folder}/{c}{r}.png', size)
    pieceset(name, folder)

# --- maurimo/chess-art "fancy" sets (MIT), SVG
for s in ['skulls', 'eyes', 'prmi', 'freak']:
    os.makedirs(f'{OUT}/pieces/{s}', exist_ok=True)
    for c in 'wb':
        for r in ROLES:
            url = f'https://raw.githubusercontent.com/maurimo/chess-art/main/fancy/{s}/{c}{r.lower()}.svg'
            open(f'{OUT}/pieces/{s}/{c}{r}.svg', 'wb').write(urllib.request.urlopen(url).read())
    pieceset(s.capitalize(), s, 'svg')

# --- Heroes Chess (Null Tale, CC-BY 4.0): demons = black (top row), humans = white
def heroes_box(color, i):
    return (i * 32, 10, i * 32 + 32, 58) if color == 'b' else (i * 32, 74, i * 32 + 32, 122)
# the sheet's header (palette, label, grass) sits above y=16: blank it
im = Image.open(f'{DL}/heroes-chess/Heroes3_Pieces.png').convert('RGBA')
im.paste((0, 0, 0, 0), (0, 0, im.width, 16))
heroes = im
for color in 'wb':
    for i, role in enumerate('PNBRQK'):
        save(heroes.crop(heroes_box(color, i)), f'{OUT}/pieces/heroes/{color}{role}.png', 192)
pieceset('Heroes', 'heroes')

# --- pixel sheets
sheet('One Bit', 'onebit', 'chess-pieces-16x16-one-bit/chess_pieces_16x16_onebit_x/pieces.png', 16, 'KQBNRP', {'b': 0, 'w': 1})
sheet('Gem Pixel', 'gempixel', 'pixel-art-chess-set/Chess Pieces Static.png', 16, 'RNBQKP', {'w': 0, 'b': 4})
sheet('Flat Pixel', 'flatpixel', 'pixel-art-chess-set/Chess Flat single color 16x.png', 16, 'NBPRKQ', {'w': 1, 'b': 3}, fix={'w': outline})
files('Spicy Pixel', 'spicypixel', 'chess-pieces/chess-pieces-png_x/color/{color}_{role}.png', 128)
files('Silver Pixel', 'silverpixel', 'pixel-art-asset-2/Chess_x/Chess/{color}_{role}.png', 128)
files('Illustrated', 'illustrated', 'chess-pack/chess-pack_x/chess-{role}-{color}.png', 256, smooth=True)

# --- boards: own SVGs (CC0)
def svg(light, dark, extra='', darkfill=None, defs=''):
    sq = ''.join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{darkfill(x, y) if darkfill else dark}"/>'
                 for y in range(8) for x in range(8) if (x + y) % 2)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8" width="1024" height="1024" shape-rendering="crispEdges">'
            f'<defs>{defs}</defs><rect width="8" height="8" fill="{light}"/>{sq}{extra}</svg>')
grid = lambda col, w, op: ''.join(f'<path d="M{i} 0V8M0 {i}H8" stroke="{col}" stroke-width="{w}" opacity="{op}"/>' for i in range(9))
boards = {
    'Neon Grid': ('#3a3270', '#1a1538', grid('#ff3ea5', .03, .8) + ''.join(f'<path d="M{i} 0V8M0 {i}H8" stroke="#3ef0ff" stroke-width=".012" opacity=".9"/>' for i in range(9)), None, ''),
    'Game Boy': ('#9bbc0f', '#306230', '', None, ''),
    'Blueprint': ('#2f6bb8', '#1d4f94', grid('#ffffff', .01, .35) + ''.join(f'<path d="M{i/4} 0V8M0 {i/4}H8" stroke="#fff" stroke-width=".004" opacity=".18"/>' for i in range(33)), None, ''),
    'Terminal': ('#1d4a26', '#0b1f10', grid('#33ff66', .015, .5), None, ''),
    'Sakura': ('#fdeef1', '#eaa0b4', '', None, ''),
    'Bauhaus': ('#f1e9d8', '#1f3d8c', '', None, ''),
    'Concrete': ('#cfcfca', '#8e8e89', '<rect width="8" height="8" filter="url(#n)" opacity=".35"/>', None,
                 '<filter id="n"><feTurbulence type="fractalNoise" baseFrequency="3" numOctaves="3"/><feColorMatrix type="saturate" values="0"/></filter>'),
    'Sunset': ('#fff4e6', '#c85a7c', '', lambda x, y: ['#ff8a5c', '#f2667a', '#d4508a', '#a8448f', '#7a3d8c', '#563a85', '#3c3576', '#2b2f63'][y],
               ''),
}
os.makedirs(f'{OUT}/boards', exist_ok=True)
for name, (light, dark, extra, df, defs) in boards.items():
    fn = name.lower().replace(' ', '-')
    open(f'{OUT}/boards/{fn}.svg', 'w').write(svg(light, dark, extra, df, defs))
    pack['board'].append({'name': name, 'image': f'boards/{fn}.svg', 'light': light, 'dark': dark})

# gchoc pixel boards (CC0): a8 is dark in the source, so mirror it
for n, name, light, dark in [(1, 'Pixel Plum', '#d5d5d5', '#413141'), (3, 'Pixel Ink', '#d5d5d5', '#000000')]:
    im = Image.open(f'{DL}/pixel-art-chess-set/CHESS ASSETS_x/CHESS ASSETS/Chess Boards/Type 2/chessBoard{n}.png').convert('RGB')
    im.transpose(Image.FLIP_LEFT_RIGHT).resize((1024, 1024), Image.NEAREST).save(f'{OUT}/boards/{name.lower().replace(" ", "-")}.png')
    pack['board'].append({'name': name, 'image': f'boards/{name.lower().replace(" ", "-")}.png', 'light': light, 'dark': dark})

json.dump(pack, open(f'{OUT}/pack.json', 'w'), indent=2)
print(len(pack['pieces']), 'piece sets,', len(pack['board']), 'boards')
