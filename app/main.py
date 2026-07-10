import tkinter as tk
from tkinter import ttk, messagebox

import db
import styles
import widgets
from cliente_view import LoginClienteFrame, CatalogoFrame
from admin_view import LoginAdminFrame, AdminFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Total Sport - Gestión de Inventario y Ventas")
        self.geometry("1120x820")
        self.minsize(1000, 720)
        styles.aplicar_estilos(self)

        self.bind("<<VolverInicio>>", lambda e: self.mostrar_inicio())

        if not self._verificar_conexion():
            self.destroy()
            return

        self.contenedor = ttk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)
        self.mostrar_inicio()

    def _verificar_conexion(self):
        try:
            db.query("SELECT 1")
            return True
        except Exception as exc:
            messagebox.showerror(
                "No se pudo conectar a la base de datos",
                f"Verifica que SQL Server esté encendido y que la base 'Tienda_Total_Sport' exista.\n\n{exc}",
            )
            return False

    def _limpiar(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self._limpiar()

        # ---- Barra promo superior ----
        promo = tk.Frame(self.contenedor, bg="#0a1122")
        promo.pack(fill="x")
        tk.Label(
            promo,
            text="⚡  SISTEMA DE GESTIÓN RETAIL  ·  INVENTARIO Y VENTAS EN TIEMPO REAL  ·  MULTI-ALMACÉN",
            bg="#0a1122", fg="#dfe6f2", font=("Segoe UI", 9, "bold"),
        ).pack(pady=6)

        # ---- Hero con gradiente ----
        hero = widgets.GradientBanner(
            self.contenedor, styles.GRAD_HERO_TOP, styles.GRAD_HERO_BOTTOM, height=195
        )
        hero.pack(fill="x")

        def _pintar_hero(_e=None):
            hero._redibujar()
            hero.delete("hero_deco")
            ancho = hero.winfo_width()
            # círculos decorativos translúcidos a la derecha
            claro = widgets.mezclar(styles.GRAD_HERO_TOP, "#ffffff", 0.14)
            claro2 = widgets.mezclar(styles.GRAD_HERO_TOP, "#ffffff", 0.08)
            hero.create_oval(ancho - 150, -90, ancho + 90, 150, outline=claro, width=2, tags="hero_deco")
            hero.create_oval(ancho - 240, -40, ancho + 40, 240, outline=claro2, width=2, tags="hero_deco")
            hero.create_oval(ancho - 70, 120, ancho + 30, 220, fill=claro2, outline="", tags="hero_deco")
            # texto
            hero.delete("hero_txt")
            hero.create_text(
                52, 88, text="🏀  TOTAL SPORT", anchor="w", fill="white",
                font=("Segoe UI", 34, "bold"), tags="hero_txt",
            )
            hero.create_text(
                54, 138, text="Gestión integrada de inventario y ventas · Retail deportivo",
                anchor="w", fill="#c3d0e4", font=("Segoe UI", 13), tags="hero_txt",
            )
            hero.tag_raise("hero_txt")

        hero.bind("<Configure>", lambda e: _pintar_hero(), add="+")
        _pintar_hero()

        # ---- Cuerpo con las dos tarjetas ----
        cuerpo = ttk.Frame(self.contenedor, padding=(40, 26))
        cuerpo.pack(expand=True, fill="both")

        ttk.Label(cuerpo, text="¿Cómo quieres ingresar?", style="Section.TLabel").pack(pady=(0, 20))

        opciones = ttk.Frame(cuerpo)
        opciones.pack()

        self._tarjeta_inicio(
            opciones, 0, "🛒", styles.COLOR_ACCENT_SOFT, "Cliente",
            "Navega el catálogo, arma tu carrito\ny confirma tu pedido en línea.",
            "Ingresar  →", styles.COLOR_ACCENT, self.mostrar_login_cliente,
        )
        self._tarjeta_inicio(
            opciones, 1, "🛠️", styles.COLOR_PRIMARY_SOFT, "Administrador",
            "Gestiona precios, inventario, pedidos\ny genera reportes ejecutivos.",
            "Ingresar  →", styles.COLOR_PRIMARY, self.mostrar_login_admin,
        )

        # ---- Fila de features ----
        features = ttk.Frame(cuerpo)
        features.pack(pady=(30, 0))
        datos_features = [
            ("🔐", "Acceso seguro", "Contraseñas con hash SHA-256"),
            ("🏬", "Multi-almacén", "Stock distribuido por tienda"),
            ("🛒", "Ventas en vivo", "Descuento automático de stock"),
            ("📄", "Reportes Word", "Indicadores ejecutivos"),
        ]
        for i, (emoji, titulo, desc) in enumerate(datos_features):
            chip = tk.Frame(features, bg=styles.COLOR_BG)
            chip.grid(row=0, column=i, padx=18)
            tk.Label(chip, text=emoji, bg=styles.COLOR_BG, font=("Segoe UI Emoji", 20)).pack()
            tk.Label(chip, text=titulo, bg=styles.COLOR_BG, fg=styles.COLOR_PRIMARY, font=("Segoe UI", 10, "bold")).pack(pady=(4, 0))
            tk.Label(chip, text=desc, bg=styles.COLOR_BG, fg=styles.COLOR_MUTED, font=("Segoe UI", 8)).pack()

        ttk.Label(
            self.contenedor,
            text="Universidad Nacional de Moquegua · Base de Datos I · Proyecto Total Sport",
            style="Footer.TLabel",
        ).pack(side="bottom", pady=12)

    def _tarjeta_inicio(self, master, col, emoji, color_circulo, titulo, descripcion, cta, color_cta, comando):
        card = widgets.HoverCard(master, on_click=comando)
        card.grid(row=0, column=col, padx=16, sticky="n")

        interior = tk.Frame(card, bg=styles.COLOR_CARD)
        interior.pack(padx=40, pady=24)
        card.registrar_hijo(interior)

        icono = widgets.crear_icono_circular(interior, emoji, color_circulo, diametro=80)
        icono.pack()
        card.registrar_hijo(icono)

        lbl_titulo = tk.Label(interior, text=titulo, bg=styles.COLOR_CARD, fg=styles.COLOR_TEXT, font=("Segoe UI", 17, "bold"))
        lbl_titulo.pack(pady=(16, 4))
        card.registrar_hijo(lbl_titulo)

        lbl_desc = tk.Label(
            interior, text=descripcion, bg=styles.COLOR_CARD, fg=styles.COLOR_MUTED,
            font=("Segoe UI", 10), justify="center",
        )
        lbl_desc.pack(pady=(0, 20))
        card.registrar_hijo(lbl_desc)

        cta_lbl = tk.Label(
            interior, text=cta, bg=color_cta, fg="white", font=("Segoe UI", 11, "bold"),
            padx=34, pady=10,
        )
        cta_lbl.pack(fill="x")
        card.registrar_hijo(cta_lbl)
        cta_lbl.bind("<Enter>", lambda e: cta_lbl.configure(bg=styles.COLOR_ACCENT_DARK if color_cta == styles.COLOR_ACCENT else styles.COLOR_PRIMARY_DARK))
        cta_lbl.bind("<Leave>", lambda e: cta_lbl.configure(bg=color_cta))

    def mostrar_login_cliente(self):
        self._limpiar()
        LoginClienteFrame(self.contenedor, on_login=self.mostrar_catalogo).pack(expand=True)

    def mostrar_catalogo(self, cliente):
        self._limpiar()
        CatalogoFrame(self.contenedor, cliente).pack(fill="both", expand=True)

    def mostrar_login_admin(self):
        self._limpiar()
        LoginAdminFrame(self.contenedor, on_login=self.mostrar_admin).pack(expand=True)

    def mostrar_admin(self):
        self._limpiar()
        AdminFrame(self.contenedor).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
