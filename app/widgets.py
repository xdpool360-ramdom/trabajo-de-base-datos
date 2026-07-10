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


def crear_icono_circular(master, emoji, color_circulo, diametro=76, bg=None):
    """Devuelve un Canvas con un círculo de color y un emoji a color centrado."""
    bg = bg or styles.COLOR_CARD
    c = tk.Canvas(master, width=diametro, height=diametro, bg=bg, highlightthickness=0, bd=0)
    c.create_oval(3, 3, diametro - 3, diametro - 3, fill=color_circulo, outline="")
    lbl = tk.Label(c, text=emoji, bg=color_circulo, font=("Segoe UI Emoji", 26))
    c.create_window(diametro / 2, diametro / 2, window=lbl)
    return c


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


class ScrollableFrame(tk.Frame):
    """Contenedor con scroll vertical (Canvas + scrollbar). Los widgets se
    colocan dentro de `.interior`. Soporta rueda del mouse."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=styles.COLOR_BG, **kwargs)
        self._canvas = tk.Canvas(self, bg=styles.COLOR_BG, highlightthickness=0, bd=0)
        self._scroll = tk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scroll.set)

        self._scroll.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self.interior = tk.Frame(self._canvas, bg=styles.COLOR_BG)
        self._win = self._canvas.create_window((0, 0), window=self.interior, anchor="nw")

        self.interior.bind("<Configure>", self._al_configurar_interior)
        self._canvas.bind("<Configure>", self._al_configurar_canvas)
        self._canvas.bind("<Enter>", lambda e: self._activar_rueda(True))
        self._canvas.bind("<Leave>", lambda e: self._activar_rueda(False))

    def _al_configurar_interior(self, _e):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _al_configurar_canvas(self, event):
        self._canvas.itemconfigure(self._win, width=event.width)

    def _activar_rueda(self, activar):
        if activar:
            self._canvas.bind_all("<MouseWheel>", self._rueda)
        else:
            self._canvas.unbind_all("<MouseWheel>")

    def _rueda(self, event):
        self._canvas.yview_scroll(int(-event.delta / 120), "units")

    def limpiar(self):
        for w in self.interior.winfo_children():
            w.destroy()
        self._canvas.yview_moveto(0)


class ProductCard(tk.Frame):
    """Tarjeta de producto estilo tienda: área de imagen (emoji + color por
    categoría), badge, nombre, marca, precio destacado y botón agregar."""

    ANCHO = 205
    ALTO = 320

    def __init__(self, master, producto, on_add):
        super().__init__(
            master, bg=styles.COLOR_CARD, highlightbackground=styles.COLOR_BORDER,
            highlightthickness=1, width=self.ANCHO, height=self.ALTO,
        )
        self._on_add = on_add
        self._producto = producto
        self.pack_propagate(False)
        self.grid_propagate(False)

        emoji, color_fondo = styles.estilo_categoria(producto.get("categoria", ""))
        stock = producto["stock"]

        # ---- Área de "imagen" ----
        imagen = tk.Frame(self, bg=color_fondo, height=140)
        imagen.pack(fill="x")
        imagen.pack_propagate(False)
        tk.Label(imagen, text=emoji, bg=color_fondo, font=("Segoe UI Emoji", 44)).place(
            relx=0.5, rely=0.5, anchor="center"
        )
        # badge de stock bajo (esquina superior izquierda)
        if stock <= 15:
            tk.Label(
                imagen, text=f" ¡Solo {stock}! ", bg=styles.COLOR_ACCENT, fg="white",
                font=("Segoe UI", 8, "bold"),
            ).place(x=8, y=8)

        # ---- Cuerpo ----
        cuerpo = tk.Frame(self, bg=styles.COLOR_CARD)
        cuerpo.pack(fill="both", expand=True, padx=12, pady=(10, 12))

        tk.Label(
            cuerpo, text=producto["marca"].upper(), bg=styles.COLOR_CARD, fg=styles.COLOR_MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

        nombre = producto["nombre"]
        tk.Label(
            cuerpo, text=nombre, bg=styles.COLOR_CARD, fg=styles.COLOR_TEXT,
            font=("Segoe UI", 10, "bold"), wraplength=self.ANCHO - 26, justify="left", height=2, anchor="nw",
        ).pack(anchor="w", fill="x", pady=(2, 2))

        tk.Label(
            cuerpo, text=f"Talla {producto['talla']} · {producto['color']}", bg=styles.COLOR_CARD,
            fg=styles.COLOR_MUTED, font=("Segoe UI", 8),
        ).pack(anchor="w")

        precio_row = tk.Frame(cuerpo, bg=styles.COLOR_CARD)
        precio_row.pack(anchor="w", pady=(6, 8))
        tk.Label(
            precio_row, text=styles.moneda(producto["precio"]), bg=styles.COLOR_CARD,
            fg=styles.COLOR_ACCENT, font=("Segoe UI", 14, "bold"),
        ).pack(side="left")

        btn = tk.Label(
            cuerpo, text="Agregar  🛒", bg=styles.COLOR_PRIMARY, fg="white",
            font=("Segoe UI", 9, "bold"), pady=7,
        )
        btn.pack(fill="x")
        btn.bind("<Button-1>", lambda e: self._on_add(self._producto))
        btn.bind("<Enter>", lambda e: btn.configure(bg=styles.COLOR_ACCENT))
        btn.bind("<Leave>", lambda e: btn.configure(bg=styles.COLOR_PRIMARY))

        # hover del borde de toda la tarjeta
        for w in (self, imagen, cuerpo):
            w.bind("<Enter>", self._hover_on, add="+")
            w.bind("<Leave>", self._hover_off, add="+")

    def _hover_on(self, _e):
        self.configure(highlightbackground=styles.COLOR_ACCENT, highlightthickness=2)

    def _hover_off(self, _e):
        self.configure(highlightbackground=styles.COLOR_BORDER, highlightthickness=1)
