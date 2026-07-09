import os
from tkinter import ttk

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

COLOR_BG = "#f1f3f8"
COLOR_PRIMARY = "#132a4c"
COLOR_PRIMARY_DARK = "#0b1c34"
COLOR_ACCENT = "#ff5a36"
COLOR_ACCENT_DARK = "#e14a28"
COLOR_TEXT = "#1c2530"
COLOR_MUTED = "#6b7688"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#dde2ea"
COLOR_SUCCESS = "#1f9d55"
COLOR_DANGER = "#d7263d"
COLOR_ROW_ALT = "#eef1f7"
COLOR_CRITICO = "#ffd9d0"

FONT_TITLE = ("Segoe UI", 30, "bold")
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_HEADER = ("Segoe UI", 15, "bold")
FONT_SECTION = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_TOTAL = ("Segoe UI", 13, "bold")


def aplicar_estilos(root):
    root.configure(bg=COLOR_BG)
    try:
        root.iconbitmap(os.path.join(_ASSETS_DIR, "icon.ico"))
    except Exception:
        pass

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=COLOR_BG)
    style.configure("Card.TFrame", background=COLOR_CARD)
    style.configure("Header.TFrame", background=COLOR_PRIMARY)

    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=FONT_BODY)
    style.configure("Card.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT, font=FONT_BODY)
    style.configure("Header.TLabel", background=COLOR_PRIMARY, foreground="white", font=FONT_HEADER)
    style.configure("Title.TLabel", background=COLOR_PRIMARY, foreground="white", font=FONT_TITLE)
    style.configure("Subtitle.TLabel", background=COLOR_PRIMARY, foreground="#c7d2e3", font=FONT_SUBTITLE)
    style.configure("Section.TLabel", background=COLOR_BG, foreground=COLOR_PRIMARY, font=FONT_SECTION)
    style.configure("Muted.TLabel", background=COLOR_BG, foreground=COLOR_MUTED, font=FONT_BODY)
    style.configure("CardMuted.TLabel", background=COLOR_CARD, foreground=COLOR_MUTED, font=FONT_BODY)
    style.configure("Total.TLabel", background=COLOR_BG, foreground=COLOR_PRIMARY, font=FONT_TOTAL)
    style.configure("Footer.TLabel", background=COLOR_BG, foreground=COLOR_MUTED, font=("Segoe UI", 8))

    style.configure(
        "Accent.TButton",
        background=COLOR_ACCENT,
        foreground="white",
        font=FONT_BUTTON,
        padding=(16, 10),
        borderwidth=0,
        focuscolor=COLOR_ACCENT,
    )
    style.map("Accent.TButton", background=[("active", COLOR_ACCENT_DARK), ("disabled", COLOR_BORDER)])

    style.configure(
        "Secondary.TButton",
        background=COLOR_PRIMARY,
        foreground="white",
        font=FONT_BUTTON,
        padding=(16, 10),
        borderwidth=0,
        focuscolor=COLOR_PRIMARY,
    )
    style.map("Secondary.TButton", background=[("active", COLOR_PRIMARY_DARK)])

    style.configure(
        "Ghost.TButton",
        background=COLOR_BG,
        foreground=COLOR_PRIMARY,
        font=FONT_BODY_BOLD,
        padding=(12, 6),
        borderwidth=1,
        relief="solid",
        bordercolor=COLOR_BORDER,
    )
    style.map("Ghost.TButton", background=[("active", COLOR_ROW_ALT)])

    style.configure("TEntry", padding=6, fieldbackground="white", bordercolor=COLOR_BORDER)
    style.configure("TSpinbox", padding=4, fieldbackground="white")
    style.configure("TCombobox", padding=4, fieldbackground="white")

    style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
    style.configure("TNotebook.Tab", font=FONT_BODY_BOLD, padding=(18, 10), background=COLOR_ROW_ALT)
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLOR_PRIMARY)],
        foreground=[("selected", "white")],
    )

    style.configure(
        "Treeview",
        background=COLOR_CARD,
        fieldbackground=COLOR_CARD,
        foreground=COLOR_TEXT,
        rowheight=28,
        font=FONT_BODY,
        borderwidth=0,
    )
    style.configure("Treeview.Heading", background=COLOR_PRIMARY, foreground="white", font=FONT_BODY_BOLD, padding=6)
    style.map(
        "Treeview.Heading",
        background=[("active", COLOR_PRIMARY_DARK)],
    )
    style.map(
        "Treeview",
        background=[("selected", COLOR_ACCENT)],
        foreground=[("selected", "white")],
    )

    style.configure("TLabelframe", background=COLOR_BG, bordercolor=COLOR_BORDER)
    style.configure("TLabelframe.Label", background=COLOR_BG, foreground=COLOR_PRIMARY, font=FONT_BODY_BOLD)


def zebra(tree):
    """Aplica franjas alternadas de color a las filas ya insertadas en un Treeview."""
    tree.tag_configure("odd", background=COLOR_ROW_ALT)
    tree.tag_configure("even", background=COLOR_CARD)
    tree.tag_configure("critico", background=COLOR_CRITICO)
    for i, iid in enumerate(tree.get_children()):
        tags = list(tree.item(iid, "tags"))
        base = "critico" if "critico" in tags else ("odd" if i % 2 else "even")
        otros = [t for t in tags if t not in ("odd", "even", "critico")]
        tree.item(iid, tags=[base] + otros)
