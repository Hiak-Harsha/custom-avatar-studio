"""
HIAK CLI Pixel Logo Generator (OpenCode & Claude Code Format)
Recreates the exact OpenCode typography with:
- 14x14 unit block pixel grid
- Signature two-tone color scheme: Gray (#808080) for 'hi' and White (#EEEEEE) for 'ak'
- Exact horizontal inset shadow band (#282828 & #434343)
- Minimalist terminal metadata layout
"""
from pathlib import Path

# Exact OpenCode Palette
BG = (10, 10, 10)         # #0A0A0A
GRAY = (128, 128, 128)     # #808080
GRAY_SHADOW = (40, 40, 40) # #282828
WHITE = (238, 238, 238)    # #EEEEEE
WHITE_SHADOW = (67, 67, 67)# #434343
_ = BG


def get_opencode_grid(mode: str = "lowercase") -> list:
    G, GS = GRAY, GRAY_SHADOW
    W, WS = WHITE, WHITE_SHADOW

    if mode == "lowercase":
        h = [
            [_, _, _, _],
            [G, _, _, _],
            [G, G, G, _],
            [G, _, _, G],
            [G, GS, GS, G],
            [G, GS, GS, G],
            [G, _, _, G],
            [_, _, _, _],
        ]
        i = [
            [_, _, _, _],
            [_, G, G, _],
            [_, _, _, _],
            [_, G, G, _],
            [_, G, G, _],
            [_, GS, GS, _],
            [_, G, G, _],
            [_, _, _, _],
        ]
        a = [
            [_, _, _, _],
            [_, _, _, _],
            [_, W, W, W],
            [_, _, _, W],
            [_, W, W, W],
            [W, WS, WS, W],
            [_, W, W, W],
            [_, _, _, _],
        ]
        k = [
            [_, _, _, _],
            [W, _, _, _],
            [W, _, _, W],
            [W, _, W, _],
            [W, W, _, _],
            [W, WS, W, _],
            [W, _, _, W],
            [_, _, _, _],
        ]
        chars = [h, i, a, k]
    else:
        # Uppercase HIAK
        H = [
            [_, _, _, _],
            [_, _, _, _],
            [W, _, _, W],
            [W, _, _, W],
            [W, W, W, W],
            [W, WS, WS, W],
            [W, _, _, W],
            [_, _, _, _],
        ]
        I = [
            [_, _, _, _],
            [_, _, _, _],
            [W, W, W, W],
            [_, W, W, _],
            [_, W, W, _],
            [_, WS, WS, _],
            [W, W, W, W],
            [_, _, _, _],
        ]
        A = [
            [_, _, _, _],
            [_, _, _, _],
            [W, W, W, W],
            [W, _, _, W],
            [W, W, W, W],
            [W, WS, WS, W],
            [W, _, _, W],
            [_, _, _, _],
        ]
        K = [
            [_, _, _, _],
            [_, _, _, _],
            [W, _, _, W],
            [W, _, W, _],
            [W, W, _, _],
            [W, WS, W, _],
            [W, _, _, W],
            [_, _, _, _],
        ]
        chars = [H, I, A, K]

    grid = []
    for r in range(8):
        row = []
        for idx, ch in enumerate(chars):
            if idx > 0:
                row.append(_)
            row.extend(ch[r])
        grid.append(row)
    return grid


def generate_hiak_cli_banner(user_name: str = "Madhav", persona: str = "Tech Creator & Coder", output_path: str = None, mode: str = "lowercase") -> str:
    grid = get_opencode_grid(mode=mode)
    lines = [""]

    meta = [
        "",
        "",
        f"    \033[1;37mhiak cli\033[0m \033[90m(v2.0)\033[0m",
        f"    \033[90m{user_name} • {persona}\033[0m",
        f"    \033[90mSystem: Windows Terminal • Windows 11\033[0m",
        f"    \033[37m~\033[0m",
        "",
        ""
    ]

    for r in range(8):
        row_str = "  "
        for c in range(len(grid[r])):
            col = grid[r][c]
            if col == BG:
                row_str += "  "
            else:
                row_str += f"\033[38;2;{col[0]};{col[1]};{col[2]}m██\033[0m"
        row_str += meta[r]
        lines.append(row_str)

    lines.append("")
    full_ansi = "\n".join(lines)

    if output_path:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(full_ansi)

    return full_ansi
