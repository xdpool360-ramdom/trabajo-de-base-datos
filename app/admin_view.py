import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import auth
import db
import styles
import widgets
import reporte_word

ESTADOS_PEDIDO = ["Todos", "Pendiente", "Pagado", "Enviado", "Entregado"]


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

        header = widgets.GradientBanner(self, styles.GRAD_TOP, styles.GRAD_BOTTOM, height=64)
        header.pack(fill="x")
        btn_cerrar = ttk.Button(
            header, text="Cerrar sesión", style="Accent.TButton",
            command=lambda: self.event_generate("<<VolverInicio>>"),
        )

        def _hdr(_e=None):
            header.delete("hdr")
            header.create_text(
                22, 32, text="🛠️  Panel de administración", anchor="w", fill="white",
                font=("Segoe UI", 15, "bold"), tags="hdr",
            )
            header.coords(win_btn, header.winfo_width() - 22, 31)

        win_btn = header.create_window(0, 0, window=btn_cerrar, anchor="e")
        header.bind("<Configure>", lambda e: (header._redibujar(e), _hdr()), add="+")
        _hdr()

        cuerpo = ttk.Frame(self, padding=15)
        cuerpo.pack(fill="both", expand=True)

        # ---- Fila de KPI cards ----
        self.kpi_row = ttk.Frame(cuerpo)
        self.kpi_row.pack(fill="x", pady=(0, 14))
        self._armar_kpis()

        notebook = ttk.Notebook(cuerpo)
        notebook.pack(fill="both", expand=True)

        self.tab_precios = ttk.Frame(notebook, style="Card.TFrame", padding=15)
        self.tab_stock = ttk.Frame(notebook, style="Card.TFrame", padding=15)
        self.tab_pedidos = ttk.Frame(notebook, style="Card.TFrame", padding=15)
        self.tab_reportes = ttk.Frame(notebook, style="Card.TFrame", padding=15)
        notebook.add(self.tab_precios, text="Precios")
        notebook.add(self.tab_stock, text="Inventario")
        notebook.add(self.tab_pedidos, text="Pedidos")
        notebook.add(self.tab_reportes, text="Reportes")

        self._armar_tab_precios()
        self._armar_tab_stock()
        self._armar_tab_pedidos()
        self._armar_tab_reportes()

    # ---------- KPI cards ----------
    def _armar_kpis(self):
        datos = db.query(
            """
            SELECT
                (SELECT COUNT(*) FROM Producto) AS productos,
                (SELECT ISNULL(SUM(total), 0) FROM Pedido) AS ventas,
                (SELECT COUNT(*) FROM Pedido) AS pedidos,
                (SELECT COUNT(*) FROM Inventario WHERE cantidad_stock < ?) AS criticos
            """,
            (db.UMBRAL_STOCK_CRITICO,),
        )[0]

        tarjetas = [
            ("Productos", str(datos["productos"]), styles.COLOR_PRIMARY, "📦"),
            ("Ventas acumuladas", styles.moneda(datos["ventas"]), styles.COLOR_SUCCESS, "💰"),
            ("Pedidos", str(datos["pedidos"]), styles.COLOR_PRIMARY, "🧾"),
            ("Alertas de stock", str(datos["criticos"]), styles.COLOR_DANGER, "⚠"),
        ]
        for i, (titulo, valor, color, emoji) in enumerate(tarjetas):
            card = widgets.crear_kpi_card(self.kpi_row, titulo, valor, color_valor=color, emoji=emoji)
            card.grid(row=0, column=i, padx=(0 if i == 0 else 10, 0), sticky="ew")
            self.kpi_row.columnconfigure(i, weight=1)

    def _refrescar_kpis(self):
        for w in self.kpi_row.winfo_children():
            w.destroy()
        self._armar_kpis()

    # ---------- Precios ----------
    def _armar_tab_precios(self):
        buscar_box = ttk.Frame(self.tab_precios, style="Card.TFrame")
        buscar_box.pack(fill="x", pady=(0, 8))
        ttk.Label(buscar_box, text="🔎 Buscar producto:", style="Card.TLabel").pack(side="left")
        self.buscar_precio_var = tk.StringVar()
        entry_buscar = ttk.Entry(buscar_box, textvariable=self.buscar_precio_var, width=30)
        entry_buscar.pack(side="left", padx=5)
        entry_buscar.bind("<KeyRelease>", lambda e: self._cargar_precios())

        cols = ("id_producto", "producto", "marca", "categoria", "precio_base")
        self.tree_precios = ttk.Treeview(self.tab_precios, columns=cols, show="headings", height=14)
        for col, ancho, titulo in [
            ("id_producto", 50, "ID"),
            ("producto", 220, "Producto"),
            ("marca", 100, "Marca"),
            ("categoria", 110, "Categoría"),
            ("precio_base", 90, "Precio"),
        ]:
            self.tree_precios.heading(col, text=titulo)
            self.tree_precios.column(col, width=ancho)
        styles.hacer_ordenable(self.tree_precios, cols)
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
        """
        params = []
        texto = self.buscar_precio_var.get().strip()
        if texto:
            sql += " WHERE p.nombre LIKE ?"
            params.append(f"%{texto}%")
        sql += " ORDER BY p.nombre"

        filas = db.query(sql, tuple(params))
        for r in filas:
            self.tree_precios.insert(
                "",
                "end",
                iid=str(r["id_producto"]),
                values=(r["id_producto"], r["producto"], r["marca"], r["categoria"], styles.moneda(r["precio_base"])),
            )
        if not filas:
            styles.mostrar_vacio(self.tree_precios, "No se encontraron productos.")
        styles.zebra(self.tree_precios)

    def _al_seleccionar_producto(self, _event):
        seleccion = self.tree_precios.selection()
        if not seleccion:
            return
        precio_actual = self.tree_precios.item(seleccion[0], "values")[4]
        self.nuevo_precio_var.set(str(precio_actual).replace("S/", "").replace(",", "").strip())

    def _guardar_precio(self):
        seleccion = self.tree_precios.selection()
        if not seleccion or not seleccion[0].isdigit():
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
        self._refrescar_kpis()

    # ---------- Inventario ----------
    def _armar_tab_stock(self):
        buscar_box = ttk.Frame(self.tab_stock, style="Card.TFrame")
        buscar_box.pack(fill="x", pady=(0, 8))
        ttk.Label(buscar_box, text="🔎 Buscar producto o SKU:", style="Card.TLabel").pack(side="left")
        self.buscar_stock_var = tk.StringVar()
        entry_buscar = ttk.Entry(buscar_box, textvariable=self.buscar_stock_var, width=30)
        entry_buscar.pack(side="left", padx=5)
        entry_buscar.bind("<KeyRelease>", lambda e: self._cargar_stock())

        self.solo_criticos_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            buscar_box, text="Solo stock crítico", variable=self.solo_criticos_var, command=self._cargar_stock
        ).pack(side="left", padx=15)

        cols = ("id_inventario", "almacen", "producto", "talla", "color", "sku", "stock")
        self.tree_stock = ttk.Treeview(self.tab_stock, columns=cols, show="headings", height=14)
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
        styles.hacer_ordenable(self.tree_stock, cols)
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
            WHERE 1=1
        """
        params = []
        texto = self.buscar_stock_var.get().strip()
        if texto:
            sql += " AND (p.nombre LIKE ? OR vp.sku LIKE ?)"
            params.extend([f"%{texto}%", f"%{texto}%"])
        if self.solo_criticos_var.get():
            sql += " AND i.cantidad_stock < ?"
            params.append(db.UMBRAL_STOCK_CRITICO)
        sql += " ORDER BY a.nombre, p.nombre"

        filas = db.query(sql, tuple(params))
        for r in filas:
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
        if not filas:
            styles.mostrar_vacio(self.tree_stock, "No se encontraron registros de inventario.")
        styles.zebra(self.tree_stock)

    def _al_seleccionar_inventario(self, _event):
        seleccion = self.tree_stock.selection()
        if not seleccion or not seleccion[0].isdigit():
            return
        stock_actual = self.tree_stock.item(seleccion[0], "values")[6]
        self.nuevo_stock_var.set(stock_actual)

    def _guardar_stock(self):
        seleccion = self.tree_stock.selection()
        if not seleccion or not seleccion[0].isdigit():
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
        self._refrescar_kpis()

    # ---------- Pedidos ----------
    def _armar_tab_pedidos(self):
        filtro_box = ttk.Frame(self.tab_pedidos, style="Card.TFrame")
        filtro_box.pack(fill="x", pady=(0, 8))
        ttk.Label(filtro_box, text="Estado:", style="Card.TLabel").pack(side="left")
        self.filtro_estado_var = tk.StringVar(value="Todos")
        combo_estado = ttk.Combobox(
            filtro_box, textvariable=self.filtro_estado_var, values=ESTADOS_PEDIDO, state="readonly", width=15
        )
        combo_estado.pack(side="left", padx=5)
        combo_estado.bind("<<ComboboxSelected>>", lambda e: self._cargar_pedidos())

        ttk.Label(filtro_box, text="Cliente:", style="Card.TLabel").pack(side="left", padx=(15, 0))
        self.buscar_pedido_var = tk.StringVar()
        entry_buscar = ttk.Entry(filtro_box, textvariable=self.buscar_pedido_var, width=25)
        entry_buscar.pack(side="left", padx=5)
        entry_buscar.bind("<KeyRelease>", lambda e: self._cargar_pedidos())

        cols_pedidos = ("id_pedido", "cliente", "fecha", "estado", "total")
        self.tree_pedidos = ttk.Treeview(self.tab_pedidos, columns=cols_pedidos, show="headings", height=12)
        for col, ancho, titulo in [
            ("id_pedido", 60, "N° Pedido"),
            ("cliente", 200, "Cliente"),
            ("fecha", 130, "Fecha"),
            ("estado", 100, "Estado"),
            ("total", 100, "Total"),
        ]:
            self.tree_pedidos.heading(col, text=titulo)
            self.tree_pedidos.column(col, width=ancho)
        styles.hacer_ordenable(self.tree_pedidos, cols_pedidos)
        self.tree_pedidos.pack(fill="both", expand=True)
        self.tree_pedidos.bind("<<TreeviewSelect>>", self._al_seleccionar_pedido)

        ttk.Label(self.tab_pedidos, text="Detalle del pedido:", style="Card.TLabel", font=styles.FONT_BODY_BOLD).pack(
            anchor="w", pady=(10, 4)
        )
        cols_detalle = ("producto", "talla", "color", "cantidad", "precio", "subtotal")
        self.tree_detalle_pedido = ttk.Treeview(self.tab_pedidos, columns=cols_detalle, show="headings", height=6)
        for col, ancho, titulo in [
            ("producto", 200, "Producto"),
            ("talla", 50, "Talla"),
            ("color", 70, "Color"),
            ("cantidad", 60, "Cant."),
            ("precio", 90, "Precio"),
            ("subtotal", 90, "Subtotal"),
        ]:
            self.tree_detalle_pedido.heading(col, text=titulo)
            self.tree_detalle_pedido.column(col, width=ancho)
        self.tree_detalle_pedido.pack(fill="both", expand=True)

        self._cargar_pedidos()

    def _cargar_pedidos(self):
        for row in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(row)
        self.tree_detalle_pedido.delete(*self.tree_detalle_pedido.get_children())

        sql = """
            SELECT ped.id_pedido, c.nombre + ' ' + c.apellido AS cliente,
                   ped.fecha_compra, ped.estado_pedido, ped.total
            FROM Pedido ped
            JOIN Cliente c ON ped.id_cliente = c.id_cliente
            WHERE 1=1
        """
        params = []
        estado = self.filtro_estado_var.get()
        if estado and estado != "Todos":
            sql += " AND ped.estado_pedido = ?"
            params.append(estado)
        texto = self.buscar_pedido_var.get().strip()
        if texto:
            sql += " AND (c.nombre + ' ' + c.apellido) LIKE ?"
            params.append(f"%{texto}%")
        sql += " ORDER BY ped.fecha_compra DESC"

        filas = db.query(sql, tuple(params))
        for r in filas:
            self.tree_pedidos.insert(
                "",
                "end",
                iid=str(r["id_pedido"]),
                values=(
                    r["id_pedido"],
                    r["cliente"],
                    r["fecha_compra"].strftime("%d/%m/%Y %H:%M"),
                    r["estado_pedido"],
                    styles.moneda(r["total"]),
                ),
            )
        if not filas:
            styles.mostrar_vacio(self.tree_pedidos, "No se encontraron pedidos con ese filtro.")
        styles.zebra(self.tree_pedidos)

    def _al_seleccionar_pedido(self, _event):
        self.tree_detalle_pedido.delete(*self.tree_detalle_pedido.get_children())
        seleccion = self.tree_pedidos.selection()
        if not seleccion or not seleccion[0].isdigit():
            return
        id_pedido = int(seleccion[0])
        sql = """
            SELECT p.nombre AS producto, vp.talla, vp.color, dp.cantidad, dp.precio_unitario
            FROM Detalle_Pedido dp
            JOIN Variante_Producto vp ON dp.id_variante = vp.id_variante
            JOIN Producto p ON vp.id_producto = p.id_producto
            WHERE dp.id_pedido = ?
        """
        for r in db.query(sql, (id_pedido,)):
            subtotal = float(r["precio_unitario"]) * r["cantidad"]
            self.tree_detalle_pedido.insert(
                "",
                "end",
                values=(
                    r["producto"],
                    r["talla"],
                    r["color"],
                    r["cantidad"],
                    styles.moneda(r["precio_unitario"]),
                    styles.moneda(subtotal),
                ),
            )
        styles.zebra(self.tree_detalle_pedido)

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
        ttk.Button(
            botones, text="📝 Generar reporte ejecutivo (Word)", style="Accent.TButton", command=self._generar_word
        ).pack(side="right", padx=3)

        self.tree_reporte = ttk.Treeview(self.tab_reportes, show="headings", height=16)
        self.tree_reporte.pack(fill="both", expand=True, pady=10)

    def _mostrar_reporte(self, columnas, titulos, filas):
        self.tree_reporte.delete(*self.tree_reporte.get_children())
        self.tree_reporte["columns"] = columnas
        for col, titulo in zip(columnas, titulos):
            self.tree_reporte.heading(col, text=titulo)
            self.tree_reporte.column(col, width=140)
        styles.hacer_ordenable(self.tree_reporte, columnas)
        for fila in filas:
            self.tree_reporte.insert("", "end", values=[fila[c] for c in columnas])
        if not filas:
            styles.mostrar_vacio(self.tree_reporte, "No hay datos para este reporte todavía.")
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
            f["total_vendido"] = styles.moneda(f["total_vendido"])
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
        fila["ventas_totales"] = styles.moneda(fila["ventas_totales"])
        self._mostrar_reporte(
            ("productos", "variantes", "unidades_stock", "clientes", "pedidos", "ventas_totales"),
            ("Productos", "Variantes", "Unid. en stock", "Clientes", "Pedidos", "Ventas totales (S/)"),
            [fila],
        )

    def _generar_word(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar reporte ejecutivo",
            defaultextension=".docx",
            filetypes=[("Documento de Word", "*.docx")],
            initialfile="Reporte_Ejecutivo_Total_Sport.docx",
        )
        if not ruta:
            return
        try:
            reporte_word.generar_reporte_ejecutivo(ruta)
        except Exception as exc:
            messagebox.showerror("Error al generar el reporte", str(exc))
            return
        if messagebox.askyesno("Reporte generado", f"El reporte se guardó en:\n{ruta}\n\n¿Quieres abrirlo ahora?"):
            os.startfile(ruta)
