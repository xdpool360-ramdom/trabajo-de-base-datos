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
        self.geometry("1080x740")
        self.minsize(980, 660)
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

        # ---- Hero con gradiente ----
        hero = widgets.GradientBanner(
            self.contenedor, styles.GRAD_HERO_TOP, styles.GRAD_HERO_BOTTOM, height=230
        )
        hero.pack(fill="x")

        def _texto_hero(_e=None):
            hero.delete("hero_txt")
            hero.create_text(
                52, 96, text="🏀  TOTAL SPORT", anchor="w", fill="white",
                font=("Segoe UI", 34, "bold"), tags="hero_txt",
            )
            hero.create_text(
                54, 148, text="Gestión integrada de inventario y ventas · Retail deportivo",
                anchor="w", fill="#c3d0e4", font=("Segoe UI", 13), tags="hero_txt",
            )

        hero.bind("<Configure>", lambda e: (hero._redibujar(e), _texto_hero()), add="+")
        _texto_hero()

        # ---- Cuerpo con las dos tarjetas ----
        cuerpo = ttk.Frame(self.contenedor, padding=(40, 30))
        cuerpo.pack(expand=True, fill="both")

        ttk.Label(cuerpo, text="¿Cómo quieres ingresar?", style="Section.TLabel").pack(pady=(0, 22))

        opciones = ttk.Frame(cuerpo)
        opciones.pack()

        self._tarjeta_inicio(
            opciones, 0, "🛒", "Cliente",
            "Navega el catálogo, arma tu carrito\ny confirma tu pedido en línea.",
            "Ingresar  →", styles.COLOR_ACCENT, self.mostrar_login_cliente,
        )
        self._tarjeta_inicio(
            opciones, 1, "🛠️", "Administrador",
            "Gestiona precios, inventario, pedidos\ny genera reportes ejecutivos.",
            "Ingresar  →", styles.COLOR_PRIMARY, self.mostrar_login_admin,
        )

        ttk.Label(
            self.contenedor,
            text="Universidad Nacional de Moquegua · Base de Datos I · Proyecto Total Sport",
            style="Footer.TLabel",
        ).pack(side="bottom", pady=12)

    def _tarjeta_inicio(self, master, col, emoji, titulo, descripcion, cta, color_cta, comando):
        card = widgets.HoverCard(master, on_click=comando)
        card.grid(row=0, column=col, padx=16, sticky="n")

        interior = tk.Frame(card, bg=styles.COLOR_CARD)
        interior.pack(padx=34, pady=28)
        card.registrar_hijo(interior)

        disco = tk.Label(
            interior,
            text=emoji,
            bg=styles.COLOR_PRIMARY_SOFT if color_cta == styles.COLOR_PRIMARY else styles.COLOR_ACCENT_SOFT,
            font=("Segoe UI", 30),
            width=3,
            height=1,
        )
        disco.pack()
        card.registrar_hijo(disco)

        lbl_titulo = tk.Label(interior, text=titulo, bg=styles.COLOR_CARD, fg=styles.COLOR_TEXT, font=("Segoe UI", 16, "bold"))
        lbl_titulo.pack(pady=(14, 4))
        card.registrar_hijo(lbl_titulo)

        lbl_desc = tk.Label(
            interior, text=descripcion, bg=styles.COLOR_CARD, fg=styles.COLOR_MUTED,
            font=("Segoe UI", 10), justify="center",
        )
        lbl_desc.pack(pady=(0, 18))
        card.registrar_hijo(lbl_desc)

        cta_lbl = tk.Label(
            interior, text=cta, bg=color_cta, fg="white", font=("Segoe UI", 11, "bold"),
            padx=28, pady=9,
        )
        cta_lbl.pack()
        card.registrar_hijo(cta_lbl)

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
