import tkinter as tk
from tkinter import ttk, messagebox

import db
import styles
from cliente_view import LoginClienteFrame, CatalogoFrame
from admin_view import LoginAdminFrame, AdminFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Total Sport - Gestión de Inventario y Ventas")
        self.geometry("1050x680")
        self.minsize(950, 600)
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

        banner = ttk.Frame(self.contenedor, style="Header.TFrame")
        banner.pack(fill="x")

        banner_contenido = ttk.Frame(banner, style="Header.TFrame", padding=(40, 55, 40, 55))
        banner_contenido.pack(fill="x")

        ttk.Label(banner_contenido, text="🏀  TOTAL SPORT", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            banner_contenido,
            text="Gestión integrada de inventario y ventas · Retail deportivo",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(6, 0))

        franja = tk.Frame(self.contenedor, bg=styles.COLOR_ACCENT, height=6)
        franja.pack(fill="x")

        cuerpo = ttk.Frame(self.contenedor, padding=40)
        cuerpo.pack(expand=True)

        ttk.Label(cuerpo, text="¿Cómo quieres ingresar?", style="Section.TLabel").pack(pady=(0, 20))

        opciones = ttk.Frame(cuerpo)
        opciones.pack()

        tarjeta_cliente = ttk.Frame(opciones, style="Card.TFrame", padding=25)
        tarjeta_cliente.grid(row=0, column=0, padx=15, sticky="n")
        ttk.Label(tarjeta_cliente, text="🛒", style="Card.TLabel", font=("Segoe UI", 28)).pack()
        ttk.Label(tarjeta_cliente, text="Cliente", style="Card.TLabel", font=styles.FONT_HEADER).pack(pady=(5, 2))
        ttk.Label(
            tarjeta_cliente,
            text="Navega el catálogo, arma tu\ncarrito y confirma tu pedido.",
            style="CardMuted.TLabel",
            justify="center",
        ).pack(pady=(0, 15))
        ttk.Button(
            tarjeta_cliente, text="Ingresar como cliente", style="Accent.TButton", command=self.mostrar_login_cliente
        ).pack(fill="x")

        tarjeta_admin = ttk.Frame(opciones, style="Card.TFrame", padding=25)
        tarjeta_admin.grid(row=0, column=1, padx=15, sticky="n")
        ttk.Label(tarjeta_admin, text="🛠️", style="Card.TLabel", font=("Segoe UI", 28)).pack()
        ttk.Label(tarjeta_admin, text="Administrador", style="Card.TLabel", font=styles.FONT_HEADER).pack(
            pady=(5, 2)
        )
        ttk.Label(
            tarjeta_admin,
            text="Gestiona precios, inventario\ny consulta reportes.",
            style="CardMuted.TLabel",
            justify="center",
        ).pack(pady=(0, 15))
        ttk.Button(
            tarjeta_admin, text="Ingresar como administrador", style="Secondary.TButton", command=self.mostrar_login_admin
        ).pack(fill="x")

        ttk.Label(
            self.contenedor,
            text="Universidad Nacional de Moquegua · Base de Datos I · Proyecto Total Sport",
            style="Footer.TLabel",
        ).pack(side="bottom", pady=12)

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
