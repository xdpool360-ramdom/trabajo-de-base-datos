import tkinter as tk
from tkinter import ttk, messagebox

import db
from cliente_view import LoginClienteFrame, CatalogoFrame
from admin_view import LoginAdminFrame, AdminFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Total Sport - Gestión de Inventario y Ventas")
        self.geometry("1000x650")
        self.minsize(900, 550)

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
        frame = ttk.Frame(self.contenedor, padding=40)
        frame.pack(expand=True)

        ttk.Label(frame, text="Total Sport", font=("Segoe UI", 24, "bold")).pack(pady=(0, 5))
        ttk.Label(frame, text="Gestión integrada de inventario y ventas", font=("Segoe UI", 11)).pack(
            pady=(0, 30)
        )

        ttk.Button(frame, text="Ingresar como cliente", width=30, command=self.mostrar_login_cliente).pack(pady=8)
        ttk.Button(frame, text="Ingresar como administrador", width=30, command=self.mostrar_login_admin).pack(
            pady=8
        )

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
