# Lichess Neo pack: Modern Mix

33 piece sets and 10 boards for [Lichess Neo](https://github.com/theophile-wallez/LichessNeo).
Import: paste this repository's link under **Packs** in the extension's settings.

## Pieces

| Set          | Source                                                                         | License   |
| ------------ | ------------------------------------------------------------------------------ | --------- |
| Skulls       | [maurimo/chess-art](https://github.com/maurimo/chess-art) (Maurizio Monge)     | MIT       |
| Eyes         | maurimo/chess-art                                                              | MIT       |
| Prmi         | maurimo/chess-art                                                              | MIT       |
| Freak        | maurimo/chess-art                                                              | MIT       |
| Heroes       | [Heroes Chess](https://nulltale.itch.io/heroes-chess) by Null Tale             | CC BY 4.0 |
| Illustrated  | [Illustrated Chess Pack](https://joszs.itch.io/chess-pack) by Joszs            | CC BY 4.0 |
| Silver Pixel | [Pixel Art Asset 2](https://greenpixels.itch.io/pixel-art-asset-2) by greenpixels | CC BY 4.0 |
| One Bit      | [Chess Pieces 16x16 One-bit](https://berryarray.itch.io/chess-pieces-16x16-one-bit) by berryarray | CC0 |
| Spicy Pixel  | [Chess Pieces](https://spicygame.itch.io/chess-pieces) by spicygame            | CC0       |
| Gem Pixel    | [Pixel Art Chess Set](https://gchoc.itch.io/pixel-art-chess-set) by Graciano Choc | CC0    |
| Flat Pixel   | Pixel Art Chess Set by Graciano Choc (outline added to white)                  | CC0       |
| Madware      | [Madware's Chess Set](https://opengameart.org/content/madwares-chess-set) by Madware | CC0  |
| GNOME Simple | [GNOME Chess](https://gitlab.gnome.org/GNOME/gnome-chess) "simple" pieces     | W3C ([notice](pieces/gnome/COPYING.html)) |
| Ivory        | [Chess pieces set](https://opengameart.org/content/chess-pieces-set) by looneybits | CC BY 3.0 |
| M484         | [M484 Chess Set](https://opengameart.org/content/m484-chess-set) by Master484  | CC BY 4.0 |
| Silhouette   | [Chess Pieces in .svg Format](https://opengameart.org/content/chess-pieces-in-svg-format) by femrek, recoloured | CC0 |
| Bauhaus      | drawn for this pack: geometric, shapes follow the moves                       | CC0       |
| Bauhaus Mono | the same without the colour accents                                            | CC0       |
| Livius       | [kmar/chess_svg_piece_sets](https://github.com/kmar/chess_svg_piece_sets) by Martin Sedlák | CC0 |
| Meridian     | kmar/chess_svg_piece_sets (meridian_shaded, after a 1952 German newspaper)     | CC0       |
| Ansuz        | [GaiusHalley/ansuz](https://github.com/GaiusHalley/ansuz)                      | CC BY-SA 4.0 |
| OpenMoji     | [OpenMoji](https://openmoji.org) chess symbols U+2654–265F                     | CC BY-SA 4.0 |
| Brilliants, Calendar, Halloween, Knights & Dragons | [WBChess](https://wbchess.com) ([Andyshark1974/ChessPieces](https://github.com/Andyshark1974/ChessPieces)) | CC BY 4.0 |
| Metaltops    | [pychess](https://github.com/pychess/pychess/tree/master/pieces/metaltops)    | GPL       |
| Pumpkins     | [BurraAbhishek/halloween-chess-piece-set](https://github.com/BurraAbhishek/halloween-chess-piece-set) | MIT |
| Font Awesome | [Font Awesome](https://fontawesome.com) free icons, recoloured                 | CC BY 4.0 |
| Tabler       | [Tabler Icons](https://tabler.io/icons), recoloured                            | MIT       |
| Material     | [Material Design Icons](https://pictogrammers.com/library/mdi/), recoloured    | Apache 2.0 |
| Lucide       | [Lucide](https://lucide.dev), recoloured                                       | ISC       |
| Game Icons   | [game-icons.net](https://game-icons.net) by Skoll, recoloured                 | CC BY 3.0 |

Pixel sets were cut from their sprite sheets and scaled up nearest-neighbour;
Illustrated was downscaled to 256px. Icon sets were filled in and recoloured
(cream with dark lines vs charcoal). Each folder that came with a license keeps it as `LICENSE.txt`. The MIT notice is in
[pieces/LICENSE-maurimo.txt](pieces/LICENSE-maurimo.txt).

## Boards

Neon Grid, Game Boy, Blueprint, Terminal, Sakura, Bauhaus, Concrete, Sunset:
drawn for this pack (SVG, CC0). Pixel Plum, Pixel Ink: Graciano Choc's
Pixel Art Chess Set (CC0), mirrored so a8 is light.

`build.py` regenerates everything from the downloaded source packs.
