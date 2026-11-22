# usage: python3 -I build.py <dl dir> <out repo dir>
import sys, os, io, json, subprocess, urllib.request
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

# --- classic-shaped sets, comfortable to play
# Madware's Chess Set (Madware, CC0): numbered 1024px tiles
mw = f"{DL}/madwares-chess-set/x/Madware's Chess Set/tiles/1024_{{:02}}.png"
for n, p in zip([1, 2, 3, 4, 5, 6, 12, 8, 13, 14, 10, 11], ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']):
    os.makedirs(f'{OUT}/pieces/madware', exist_ok=True)
    Image.open(mw.format(n)).convert('RGBA').resize((256, 256), Image.LANCZOS).save(f'{OUT}/pieces/madware/{p}.png')
pieceset('Madware', 'madware')

# GNOME Chess "simple" (W3C license), SVG
os.makedirs(f'{OUT}/pieces/gnome', exist_ok=True)
for c, cn in (('w', 'white'), ('b', 'black')):
    for r in ROLES:
        open(f'{OUT}/pieces/gnome/{c}{r}.svg', 'wb').write(open(f'{DL}/gnome/simple/{cn}{NAMES[r].capitalize()}.svg', 'rb').read())
pieceset('GNOME Simple', 'gnome', 'svg')

# looneybits' chess pieces set (CC BY 3.0): two 6-piece strips, P R N B Q K
for c in 'wb':
    im = Image.open(f'{DL}/chess-pieces-set/chess_pieces_{"white" if c == "w" else "black"}.png').convert('RGBA')
    w = im.width // 6
    top = im.getbbox()[1]; im = im.crop((0, max(0, top - 4), im.width, im.height))  # drop empty space above the king
    for i, r in enumerate('PRNBQK'):
        crop = im.crop((i * w, 0, i * w + w, im.height))
        s2 = max(crop.size); sq = Image.new('RGBA', (s2, s2)); sq.paste(crop, ((s2 - crop.width) // 2, s2 - crop.height))
        os.makedirs(f'{OUT}/pieces/ivory', exist_ok=True)
        sq.resize((256, 256), Image.LANCZOS).save(f'{OUT}/pieces/ivory/{c}{r}.png')
pieceset('Ivory', 'ivory')

# M484 (Master484, CC BY 4.0): 26px cells, step 27, opaque blue background
def m484_clear(img):
    img.putdata([(0, 0, 0, 0) if p[:3] == (119, 153, 187) else p for p in img.get_flattened_data()]); return img
sheet('M484', 'm484', 'm484-chess-set/chess_pieces_v5.png', 27, 'KQRBNP', {'w': 0, 'b': 1}, size=208,
      box=lambda c, i: (5 + 27 * i, 8 if c == 'w' else 38, 31 + 27 * i, 34 if c == 'w' else 64),
      fix={'w': m484_clear, 'b': m484_clear})

# femrek's single-colour SVG silhouettes (CC0), recoloured: cream with an outline vs charcoal
for c in 'wb':
    for r, f in zip(ROLES, ['king_1', 'queen', 'rok', 'bishop_0', 'knight_3', 'pawn']):
        png = subprocess.run(['rsvg-convert', '-w', '216', '-h', '216', '--keep-aspect-ratio', f'{DL}/chess-pieces-in-svg-format/{f}.svg'], capture_output=True, check=True).stdout
        a = Image.open(io.BytesIO(png)).convert('RGBA').getchannel('A')
        body = Image.new('RGBA', a.size, (245, 241, 233, 255) if c == 'w' else (36, 38, 43, 255)); body.putalpha(a)
        if c == 'w':
            body = outline(body)  # 1px is too thin at this size: grow twice more
            body = outline(outline(body.crop((1, 1, body.width - 1, body.height - 1))))
        save(body, f'{OUT}/pieces/silhouette/{c}{r}.png', 256)
pieceset('Silhouette', 'silhouette')

# --- Bauhaus: own geometric set (CC0). Shapes follow the moves: L knight, diagonal bishop, round queen.
SHAPES = {
    'P': '<rect x="33" y="56" width="34" height="34"/>',
    'R': '<rect x="27" y="34" width="46" height="56"/>',
    'N': '<path d="M27 90H73V64H51V28H27Z"/><rect class="a" x="27" y="28" width="24" height="18"/>',
    'B': '<rect x="32" y="72" width="36" height="18"/><path class="a" d="M50 20L75 46L50 72L25 46Z"/>',
    'Q': '<rect x="29" y="64" width="42" height="26"/><circle class="a" cx="50" cy="42" r="21"/>',
    'K': '<rect x="27" y="60" width="46" height="30"/><path class="a" d="M50 18L71 39L50 60L29 39Z"/><rect x="45" y="6" width="10" height="16"/>',
}
ACCENT = dict(P='', R='', N='#d63b2a', B='#2347a0', Q='#d63b2a', K='#f2b705')
for folder, name, accents in (('bauhaus', 'Bauhaus', True), ('bauhausmono', 'Bauhaus Mono', False)):
    os.makedirs(f'{OUT}/pieces/{folder}', exist_ok=True)
    for c, body, line in (('w', '#f1ebdd', '#1a1a1a'), ('b', '#232326', '#000000')):
        for r in ROLES:
            acc = ACCENT[r] if accents and ACCENT[r] else body
            open(f'{OUT}/pieces/{folder}/{c}{r}.svg', 'w').write(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="7 3 86 90"><style>*{{fill:{body};stroke:{line};stroke-width:3.5;stroke-linejoin:miter}}.a{{fill:{acc}}}</style>{SHAPES[r]}</svg>')
    pieceset(name, folder, 'svg')

# --- ready-made SVG sets, copied as they are (sources and licenses in README / each folder's LICENSE.txt)
C = f'{DL}/cand'
import shutil
for folder, name in [('livius', 'Livius'), ('meridian_shaded', 'Meridian'), ('ansuz', 'Ansuz'), ('openmoji', 'OpenMoji'),
                     ('wb_Brilliants', 'Brilliants'), ('wb_Calendar', 'Calendar'), ('wb_Halloween', 'Halloween'),
                     ('wb_Knights_and_Dragons', 'Knights & Dragons'), ('metaltops', 'Metaltops'), ('halloween_burra', 'Pumpkins')]:
    out = folder.lower().replace('wb_', '').replace('_', '')
    shutil.copytree(f'{C}/{folder}', f'{OUT}/pieces/{out}')
    if os.path.exists(f'{C}/licenses/{folder}.txt'): shutil.copy(f'{C}/licenses/{folder}.txt', f'{OUT}/pieces/{out}/LICENSE.txt')
    pieceset(name, out, 'svg')

# --- single-colour icon sets, recoloured: cream body with dark lines vs charcoal body
CREAM, INK, CHAR, GREY = (245, 241, 233, 255), (30, 30, 36, 255), (36, 38, 43, 255), (150, 154, 162, 255)
def alpha(svgfile, px=224, strip_bg=False):
    data = open(svgfile, 'rb').read()
    if strip_bg: data = data.replace(b'<path d="M0 0h512v512H0z"/>', b'')
    png = subprocess.run(['rsvg-convert', '-w', str(px), '-h', str(px), '--keep-aspect-ratio', '-'], input=data, capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert('RGBA').getchannel('A')
def filled(a):
    """Silhouette of a line icon: everything not reachable from the border."""
    from PIL import ImageDraw, ImageChops
    m = a.point(lambda v: 255 if v > 64 else 0).convert('L')
    big = Image.new('L', (m.width + 2, m.height + 2)); big.paste(m, (1, 1))
    ImageDraw.floodfill(big, (0, 0), 128)
    inside = big.point(lambda v: 0 if v == 128 else 255).crop((1, 1, m.width + 1, m.height + 1))
    return ImageChops.lighter(inside, a)
def layer(mask, color):
    im = Image.new('RGBA', mask.size, color); im.putalpha(mask); return im
def place(im, path):
    """Icons fill their whole box: give them a margin, bottom-heavy like real pieces."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sq = Image.new('RGBA', (256, 256)); sq.paste(im, ((256 - im.width) // 2, 256 - im.height - 10), im); sq.save(path)
def svgsrc(pattern, strip_bg=False):
    return lambda r: alpha(pattern.format(role=r), strip_bg=strip_bg)
def glyphsrc(fontfile, first):
    """Unicode chess glyphs (U+2654 white king … ) from a font, all on one baseline so relative sizes hold."""
    from PIL import ImageFont, ImageDraw
    font = ImageFont.truetype(fontfile, 210)
    def src(r):
        im = Image.new('L', (224, 224)); ImageDraw.Draw(im).text((112, 206), chr(first + 'KQRBNP'.index(r)), font=font, fill=255, anchor='ms')
        return im
    return src
def iconset(name, folder, line=None, solid=None):
    """line: outlined glyph, filled in for the body (white, and black when there is no solid one);
    solid: filled glyph for black (its cut-out details turn grey), or both sides when there is no line one."""
    from PIL import ImageChops
    for r in ROLES:
        l = line(r) if line else None
        s = solid(r) if solid else None
        if l is None:  # solid only: a grown silhouette makes white's outline
            ring = s.filter(ImageFilter.MaxFilter(7))
            w = Image.alpha_composite(layer(ring, INK), layer(s, CREAM))
        else:
            w = Image.alpha_composite(layer(filled(l), CREAM), layer(l, INK))
        if s is not None:
            b = Image.alpha_composite(layer(filled(s), GREY), layer(s, CHAR))
        else:
            body = filled(l)
            inner = ImageChops.multiply(l, body.filter(ImageFilter.MinFilter(29)).filter(ImageFilter.MinFilter(29)))  # drop the outer contour
            b = Image.alpha_composite(layer(body, CHAR), layer(inner, GREY))
        place(w, f'{OUT}/pieces/{folder}/w{r}.png'); place(b, f'{OUT}/pieces/{folder}/b{r}.png')
    pieceset(name, folder)
I = f'{DL}/ic'
iconset('Font Awesome', 'fontawesome', line=svgsrc(f'{C}/fa_reg/{{role}}.svg'))
iconset('Tabler', 'tabler', line=svgsrc(f'{C}/tabler_o/{{role}}.svg'))
iconset('Material', 'material', solid=svgsrc(f'{C}/mdi/{{role}}.svg'))
iconset('Lucide', 'lucide', line=svgsrc(f'{C}/lucide/{{role}}.svg'))
iconset('Game Icons', 'gameicons', solid=svgsrc(f'{C}/gameicons/{{role}}.svg', strip_bg=True))
iconset('Boxicons', 'boxicons', line=svgsrc(f'{I}/boxicons/{{role}}.svg'), solid=svgsrc(f'{I}/boxicons-filled/{{role}}.svg'))
iconset('Material Symbols', 'materialsymbols', line=svgsrc(f'{I}/material-symbols-outline-rounded/{{role}}.svg'), solid=svgsrc(f'{I}/material-symbols-rounded/{{role}}.svg'))
iconset('Hugeicons', 'hugeicons', line=svgsrc(f'{I}/hugeicons/{{role}}.svg'))
iconset('Iconoven', 'iconoven', line=svgsrc(f'{I}/iconoven/{{role}}.svg'))
iconset('Line Awesome', 'lineawesome', line=svgsrc(f'{I}/la/{{role}}.svg'))
iconset('Noto', 'noto', line=glyphsrc(f'{DL}/fonts/NotoSansSymbols2.ttf', 0x2654), solid=glyphsrc(f'{DL}/fonts/NotoSansSymbols2.ttf', 0x265A))
iconset('DejaVu', 'dejavu', line=glyphsrc(f'{DL}/fonts/DejaVuSans.ttf', 0x2654), solid=glyphsrc(f'{DL}/fonts/DejaVuSans.ttf', 0x265A))
for folder, text in [('boxicons', 'Boxicons, https://boxicons.com, MIT'), ('materialsymbols', 'Material Symbols by Google, Apache License 2.0'),
                     ('hugeicons', 'Hugeicons free, https://hugeicons.com, MIT'), ('iconoven', 'IconOven, MIT'),
                     ('lineawesome', 'Line Awesome by Icons8, Apache License 2.0')]:
    open(f'{OUT}/pieces/{folder}/LICENSE.txt', 'w').write(text + '\nObtained through Iconify (https://iconify.design); recoloured for this pack.\n')
shutil.copy(f'{DL}/fonts/OFL-noto.txt', f'{OUT}/pieces/noto/LICENSE.txt')
shutil.copy(f'{DL}/fonts/LICENSE', f'{OUT}/pieces/dejavu/LICENSE.txt')
for folder, lic in [('fontawesome', 'fontawesome'), ('tabler', 'tabler'), ('material', 'mdi'), ('lucide', 'lucide'), ('gameicons', 'gameicons')]:
    shutil.copy(f'{C}/licenses/{lic}.txt', f'{OUT}/pieces/{folder}/LICENSE.txt')

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

# editor colour schemes (palettes only, drawn here; CC0)
EDITORS = {
    'Catppuccin': ('#b4befe', '#45475a'), 'Nord': ('#d8dee9', '#5e81ac'), 'Dracula': ('#bd93f9', '#44475a'),
    'Gruvbox': ('#ebdbb2', '#458588'), 'Solarized': ('#fdf6e3', '#2aa198'), 'Tokyo Night': ('#c0caf5', '#3d59a1'),
    'Rose Pine': ('#ebbcba', '#31748f'), 'Everforest': ('#e6e2cc', '#93b259'), 'Kanagawa': ('#dcd7ba', '#7e9cd8'),
    'One Dark': ('#abb2bf', '#4b5263'),
}
for name, (light, dark) in EDITORS.items():
    fn = 'editor-' + name.lower().replace(' ', '-')
    open(f'{OUT}/boards/{fn}.svg', 'w').write(svg(light, dark))
    pack['board'].append({'name': name, 'image': f'boards/{fn}.svg', 'light': light, 'dark': dark})

# stone and leather from ambientCG textures (CC0): each square a different patch of the texture
import random
from PIL import ImageStat
def texboard(name, a, b):
    tex = {k: Image.open(f'{DL}/acgtex/{k}/{k}_1K-JPG_Color.jpg').convert('RGB') for k in (a, b)}
    rnd = random.Random(a + b)
    im = Image.new('RGB', (1024, 1024))
    for y in range(8):
        for x in range(8):
            t = tex[a if (x + y) % 2 == 0 else b]
            ox, oy = rnd.randrange(t.width - 128), rnd.randrange(t.height - 128)
            im.paste(t.crop((ox, oy, ox + 128, oy + 128)), (x * 128, y * 128))
    fn = f'boards/{name.lower().replace(" ", "-").replace("&", "and")}.jpg'
    im.save(f'{OUT}/{fn}', quality=88)
    mean = lambda k: '#%02x%02x%02x' % tuple(int(v) for v in ImageStat.Stat(tex[k]).mean)
    pack['board'].append({'name': name, 'image': fn, 'light': mean(a), 'dark': mean(b)})
for name, a, b in [('Terrazzo Navy', 'Terrazzo011', 'Terrazzo015'), ('Terrazzo Green', 'Terrazzo009', 'Terrazzo016'),
                   ('Granite', 'Granite002A', 'Fabric004'), ('Onyx & Leather', 'Onyx004', 'Leather030'),
                   ('Travertine', 'Travertine009', 'Travertine005'), ('Travertine Noir', 'Travertine009', 'Leather026')]:
    texboard(name, a, b)

json.dump(pack, open(f'{OUT}/pack.json', 'w'), indent=2)
print(len(pack['pieces']), 'piece sets,', len(pack['board']), 'boards')
