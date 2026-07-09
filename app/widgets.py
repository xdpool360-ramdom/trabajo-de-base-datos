import tkinter as tk

import styles


def _hex_a_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_a_hex(rgb):
    return "#%02x%02x%02x" % rgb


def mezclar(color_a, color_b, t):
    """Interpola dos colores hex. t=0 -> color_a, t=1 -> color_b."""
    ra, ga, ba = _hex_a_rgb(color_a)
    rb, gb, bb = _hex_a_rgb(color_b)
    return _rgb_a_hex(
        (
            int(ra + (rb - ra) * t),
            int(ga + (gb - ga) * t),
            int(ba + (bb - ba) * t),
        )
    )


class GradientBanner(tk.Canvas):
    """Banner con gradiente vertical dibujado sobre un Canvas.

    Permite colocar widgets encima usando create_window a través de add_widget.
    Se redibuja automáticamente al cambiar de tamaño.
    """

    def __init__(self, master, color_top, color_bottom, height=140, **kwargs):
        super().__init__(master, height=height, highlightthickness=0, bd=0, **kwargs)
        self._top = color_top
        self._bottom = color_bottom
        self._alto = height
        self._items_texto = []  # (id, x_rel, y, ...) para reposicionar
        self.bind("<Configure>", self._redibujar)

    def _redibujar(self, event=None):
        self.delete("grad")
        ancho = self.winfo_width()
        alto = self.winfo_height()
        pasos = max(alto, 1)
        for i in range(pasos):
            t = i / pasos
            color = mezclar(self._top, self._bottom, t)
            self.create_line(0, i, ancho, i, fill=color, tags="grad")
        # una fina línea de acento en la base
        self.create_line(0, alto - 3, ancho, alto - 3, fill=styles.COLOR_ACCENT, width=3, tags="grad")
        self.tag_lower("grad")


def crear_kpi_card(master, titulo, valor, color_valor=None, emoji=""):
    """Tarjeta de métrica: número grande + etiqueta, sobre fondo blanco."""
    color_valor = color_valor or styles.COLOR_PRIMARY
    card = tk.Frame(master, bg=styles.COLOR_CARD, highlightbackground=styles.COLOR_BORDER, highlightthickness=1)
    interior = tk.Frame(card, bg=styles.COLOR_CARD)
    interior.pack(padx=18, pady=14, anchor="w")

    fila_top = tk.Frame(interior, bg=styles.COLOR_CARD)
    fila_top.pack(anchor="w")
    if emoji:
        tk.Label(fila_top, text=emoji, bg=styles.COLOR_CARD, font=("Segoe UI", 16)).pack(side="left", padx=(0, 6))
    lbl_valor = tk.Label(
        fila_top, text=str(valor), bg=styles.COLOR_CARD, fg=color_valor, font=("Segoe UI", 22, "bold")
    )
    lbl_valor.pack(side="left")

    tk.Label(
        interior, text=titulo, bg=styles.COLOR_CARD, fg=styles.COLOR_MUTED, font=("Segoe UI", 9)
    ).pack(anchor="w", pady=(2, 0))

    card.valor_label = lbl_valor  # para poder actualizar el número luego
    return card


class HoverCard(tk.Frame):
    """Tarjeta clicable con borde que resalta al pasar el mouse."""

    def __init__(self, master, on_click=None, **kwargs):
        super().__init__(
            master,
            bg=styles.COLOR_CARD,
            highlightbackground=styles.COLOR_BORDER,
            highlightthickness=1,
            **kwargs,
        )
        self._on_click = on_click
        self._enlazar(self)

    def _enlazar(self, widget):
        widget.bind("<Enter>", self._al_entrar, add="+")
        widget.bind("<Leave>", self._al_salir, add="+")
        if self._on_click:
            widget.bind("<Button-1>", lambda e: self._on_click(), add="+")

    def registrar_hijo(self, widget):
        """Propaga los eventos de hover/clic a los hijos internos."""
        self._enlazar(widget)

    def _al_entrar(self, _e):
        self.configure(highlightbackground=styles.COLOR_ACCENT, highlightthickness=2)

    def _al_salir(self, _e):
        self.configure(highlightbackground=styles.COLOR_BORDER, highlightthickness=1)
