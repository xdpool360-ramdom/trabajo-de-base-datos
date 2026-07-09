import tkinter as tk
from tkinter import ttk, messagebox

import auth
import db
import styles


class LoginAdminFrame(ttk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master, padding=30)
        self.on_login = on_login

        ttk.Label(self, text="🛠️  Acceso de administrador", style="Section.TLabel", font=styles.FONT_HEADER).pack(
            pady=(0, 20)
        )

        tarjeta = ttk.Frame(self, style="Card.TFrame", padding=25)
        tarjeta.pack()

        ttk.Label(tarjeta, text="Usuario:", style="Card.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        self.user_var = tk.StringVar()
        entry_user = ttk.Entry(tarjeta, textvariable=self.user_var, width=30)
        entry_user.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        entry_user.focus()

        ttk.Label(tarjeta, text="Contraseña:", style="Card.TLabel").grid(row=2, column=0, columnspan=2, sticky="w")
        self.pass_var = tk.StringVar()
        entry = ttk.Entry(tarjeta, textvariable=self.pass_var, show="*", width=30)
        entry.grid(row=3, column=0, columnspan=2, pady=(0, 15))
        entry.bind("<Return>", lambda e: self._login())

        ttk.Button(tarjeta, text="Ingresar", style="Accent.TButton", command=self._login).grid(
            row=4, column=0, sticky="ew", padx=(0, 5)
        )
        ttk.Button(
            tarjeta, text="Volver", style="Ghost.TButton", command=lambda: self.master.event_generate("<<VolverInicio>>")
        ).grid(row=4, column=1, sticky="ew", padx=(5, 0))

    def _login(self):
        username = self.user_var.get().strip()
        password = self.pass_var.get()
        if not username or not password:
            messagebox.showwarning("Faltan datos", "Escribe tu usuario y contraseña.")
            return

        rows = db.query("SELECT * FROM Usuario WHERE username = ? AND rol = 'admin'", (username,))
        if not rows or not auth.verificar_password(password, rows[0]["salt"], rows[0]["password_hash"]):
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
            return
        self.on_login()


class AdminFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=0)

        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 14))
        header.pack(fill="x")
        ttk.Label(header, text="🛠️  Panel de administración", style="Header.TLabel").pack(side="left")
        ttk.Button(
            header, text="Cerrar sesión", style="Accent.TButton", command=lambda: self.event_generate("<<VolverInicio>>")
        ).pack(side="right")

        cuerpo = ttk.Frame(self, padding=15)
        cuerpo.pack(fill="both", expand=True)

        notebook = ttk.Notebook(cuerpo)
        notebook.pack(fill="both", expand=True)

        self.tab_precios = ttk.Frame(notebook, style="Card.TFrame", padding=15)
        self.tab_stock = ttk.Frame(notebook, style="Card.TFrame", padding=15)
        self.tab_reportes = ttk.Frame(notebook, style="Card.TFrame", padding=15)
        notebook.add(self.tab_precios, text="Precios")
        notebook.add(self.tab_stock, text="Inventario")
        notebook.add(self.tab_reportes, text="Reportes")

        self._armar_tab_precios()
        self._armar_tab_stock()
        self._armar_tab_reportes()

    # ---------- Precios ----------
    def _armar_tab_precios(self):
        cols = ("id_producto", "producto", "marca", "categoria", "precio_base")
        self.tree_precios = ttk.Treeview(self.tab_precios, columns=cols, show="headings", height=16)
        for col, ancho, titulo in [
            ("id_producto", 50, "ID"),
            ("producto", 220, "Producto"),
            ("marca", 100, "Marca"),
            ("categoria", 110, "Categoría"),
            ("precio_base", 90, "Precio"),
        ]:
            self.tree_precios.heading(col, text=titulo)
            self.tree_precios.column(col, width=ancho)
        self.tree_precios.pack(fill="both", expand=True)
        self.tree_precios.bind("<<TreeviewSelect>>", self._al_seleccionar_producto)

        pie = ttk.Frame(self.tab_precios, style="Card.TFrame")
        pie.pack(fill="x", pady=8)
        ttk.Label(pie, text="Nuevo precio (S/):", style="Card.TLabel").pack(side="left")
        self.nuevo_precio_var = tk.StringVar()
        ttk.Entry(pie, textvariable=self.nuevo_precio_var, width=12).pack(side="left", padx=5)
        ttk.Button(pie, text="Guardar precio", style="Accent.TButton", command=self._guardar_precio).pack(
            side="left", padx=5
        )
        ttk.Button(pie, text="Actualizar lista", style="Ghost.TButton", command=self._cargar_precios).pack(
            side="right"
        )

        self._cargar_precios()

    def _cargar_precios(self):
        for row in self.tree_precios.get_children():
            self.tree_precios.delete(row)
        sql = """
            SELECT p.id_producto, p.nombre AS producto, m.nombre AS marca,
                   c.nombre AS categoria, p.precio_base
            FROM Producto p
            JOIN Marca m ON p.id_marca = m.id_marca
            JOIN Categoria c ON p.id_categoria = c.id_categoria
            ORDER BY p.nombre
        """
        for r in db.query(sql):
            self.tree_precios.insert(
                "",
                "end",
                iid=str(r["id_producto"]),
                values=(r["id_producto"], r["producto"], r["marca"], r["categoria"], f"{r['precio_base']:.2f}"),
            )
        styles.zebra(self.tree_precios)

    def _al_seleccionar_producto(self, _event):
        seleccion = self.tree_precios.selection()
        if not seleccion:
            return
        precio_actual = self.tree_precios.item(seleccion[0], "values")[4]
        self.nuevo_precio_var.set(precio_actual)

    def _guardar_precio(self):
        seleccion = self.tree_precios.selection()
        if not seleccion:
            messagebox.showinfo("Selecciona un producto", "Elige un producto de la lista.")
            return
        try:
            nuevo_precio = float(self.nuevo_precio_var.get())
            if nuevo_precio < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Precio inválido", "Ingresa un número válido mayor o igual a 0.")
            return

        id_producto = int(seleccion[0])
        db.execute("UPDATE Producto SET precio_base = ? WHERE id_producto = ?", (nuevo_precio, id_producto))
        messagebox.showinfo("Precio actualizado", "El precio se guardó correctamente.")
        self._cargar_precios()

    # ---------- Inventario ----------
    def _armar_tab_stock(self):
        cols = ("id_inventario", "almacen", "producto", "talla", "color", "sku", "stock")
        self.tree_stock = ttk.Treeview(self.tab_stock, columns=cols, show="headings", height=16)
        for col, ancho, titulo in [
            ("id_inventario", 50, "ID"),
            ("almacen", 130, "Almacén"),
            ("producto", 180, "Producto"),
            ("talla", 50, "Talla"),
            ("color", 70, "Color"),
            ("sku", 130, "SKU"),
            ("stock", 60, "Stock"),
        ]:
            self.tree_stock.heading(col, text=titulo)
            self.tree_stock.column(col, width=ancho)
        self.tree_stock.pack(fill="both", expand=True)
        self.tree_stock.bind("<<TreeviewSelect>>", self._al_seleccionar_inventario)

        pie = ttk.Frame(self.tab_stock, style="Card.TFrame")
        pie.pack(fill="x", pady=8)
        ttk.Label(pie, text=f"Nuevo stock (umbral crítico: {db.UMBRAL_STOCK_CRITICO}):", style="Card.TLabel").pack(
            side="left"
        )
        self.nuevo_stock_var = tk.StringVar()
        ttk.Entry(pie, textvariable=self.nuevo_stock_var, width=10).pack(side="left", padx=5)
        ttk.Button(pie, text="Guardar stock", style="Accent.TButton", command=self._guardar_stock).pack(
            side="left", padx=5
        )
        ttk.Button(pie, text="Actualizar lista", style="Ghost.TButton", command=self._cargar_stock).pack(
            side="right"
        )

        self._cargar_stock()

    def _cargar_stock(self):
        for row in self.tree_stock.get_children():
            self.tree_stock.delete(row)
        sql = """
            SELECT i.id_inventario, a.nombre AS almacen, p.nombre AS producto,
                   vp.talla, vp.color, vp.sku, i.cantidad_stock
            FROM Inventario i
            JOIN Almacen a ON i.id_almacen = a.id_almacen
            JOIN Variante_Producto vp ON i.id_variante = vp.id_variante
            JOIN Producto p ON vp.id_producto = p.id_producto
            ORDER BY a.nombre, p.nombre
        """
        for r in db.query(sql):
            tags = ("critico",) if r["cantidad_stock"] < db.UMBRAL_STOCK_CRITICO else ()
            self.tree_stock.insert(
                "",
                "end",
                iid=str(r["id_inventario"]),
                values=(
                    r["id_inventario"],
                    r["almacen"],
                    r["producto"],
                    r["talla"],
                    r["color"],
                    r["sku"],
                    r["cantidad_stock"],
                ),
                tags=tags,
            )
        styles.zebra(self.tree_stock)

    def _al_seleccionar_inventario(self, _event):
        seleccion = self.tree_stock.selection()
        if not seleccion:
            return
        stock_actual = self.tree_stock.item(seleccion[0], "values")[6]
        self.nuevo_stock_var.set(stock_actual)

    def _guardar_stock(self):
        seleccion = self.tree_stock.selection()
        if not seleccion:
            messagebox.showinfo("Selecciona un registro", "Elige una fila de inventario.")
            return
        try:
            nuevo_stock = int(self.nuevo_stock_var.get())
            if nuevo_stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Stock inválido", "Ingresa un número entero mayor o igual a 0.")
            return

        id_inventario = int(seleccion[0])
        db.execute(
            "UPDATE Inventario SET cantidad_stock = ?, fecha_ultima_actualizacion = GETDATE() "
            "WHERE id_inventario = ?",
            (nuevo_stock, id_inventario),
        )
        messagebox.showinfo("Stock actualizado", "El stock se guardó correctamente.")
        self._cargar_stock()

    # ---------- Reportes ----------
    def _armar_tab_reportes(self):
        botones = ttk.Frame(self.tab_reportes, style="Card.TFrame")
        botones.pack(fill="x")
        ttk.Button(
            botones, text="⚠ Stock crítico", style="Secondary.TButton", command=self._reporte_stock_critico
        ).pack(side="left", padx=3)
        ttk.Button(
            botones,
            text="📈 Ventas por producto",
            style="Secondary.TButton",
            command=self._reporte_ventas_producto,
        ).pack(side="left", padx=3)
        ttk.Button(
            botones, text="📊 Resumen general", style="Secondary.TButton", command=self._reporte_resumen
        ).pack(side="left", padx=3)

        self.tree_reporte = ttk.Treeview(self.tab_reportes, show="headings", height=16)
        self.tree_reporte.pack(fill="both", expand=True, pady=10)

    def _mostrar_reporte(self, columnas, titulos, filas):
        self.tree_reporte.delete(*self.tree_reporte.get_children())
        self.tree_reporte["columns"] = columnas
        for col, titulo in zip(columnas, titulos):
            self.tree_reporte.heading(col, text=titulo)
            self.tree_reporte.column(col, width=140)
        for fila in filas:
            self.tree_reporte.insert("", "end", values=[fila[c] for c in columnas])
        styles.zebra(self.tree_reporte)

    def _reporte_stock_critico(self):
        sql = """
            SELECT a.nombre AS almacen, p.nombre AS producto, vp.sku, i.cantidad_stock AS stock
            FROM Inventario i
            JOIN Almacen a ON i.id_almacen = a.id_almacen
            JOIN Variante_Producto vp ON i.id_variante = vp.id_variante
            JOIN Producto p ON vp.id_producto = p.id_producto
            WHERE i.cantidad_stock < ?
            ORDER BY i.cantidad_stock ASC
        """
        filas = db.query(sql, (db.UMBRAL_STOCK_CRITICO,))
        self._mostrar_reporte(
            ("almacen", "producto", "sku", "stock"), ("Almacén", "Producto", "SKU", "Stock"), filas
        )

    def _reporte_ventas_producto(self):
        sql = """
            SELECT p.nombre AS producto, SUM(dp.cantidad) AS unidades_vendidas,
                   SUM(dp.cantidad * dp.precio_unitario) AS total_vendido
            FROM Detalle_Pedido dp
            JOIN Variante_Producto vp ON dp.id_variante = vp.id_variante
            JOIN Producto p ON vp.id_producto = p.id_producto
            GROUP BY p.nombre
            ORDER BY total_vendido DESC
        """
        filas = db.query(sql)
        for f in filas:
            f["total_vendido"] = f"{f['total_vendido']:.2f}"
        self._mostrar_reporte(
            ("producto", "unidades_vendidas", "total_vendido"),
            ("Producto", "Unidades vendidas", "Total vendido (S/)"),
            filas,
        )

    def _reporte_resumen(self):
        sql = """
            SELECT
                (SELECT COUNT(*) FROM Producto) AS productos,
                (SELECT COUNT(*) FROM Variante_Producto) AS variantes,
                (SELECT SUM(cantidad_stock) FROM Inventario) AS unidades_stock,
                (SELECT COUNT(*) FROM Cliente) AS clientes,
                (SELECT COUNT(*) FROM Pedido) AS pedidos,
                (SELECT ISNULL(SUM(total), 0) FROM Pedido) AS ventas_totales
        """
        fila = db.query(sql)[0]
        fila["ventas_totales"] = f"{fila['ventas_totales']:.2f}"
        self._mostrar_reporte(
            ("productos", "variantes", "unidades_stock", "clientes", "pedidos", "ventas_totales"),
            ("Productos", "Variantes", "Unid. en stock", "Clientes", "Pedidos", "Ventas totales (S/)"),
            [fila],
        )
