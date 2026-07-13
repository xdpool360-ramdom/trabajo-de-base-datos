import tkinter as tk
from tkinter import ttk, messagebox

import auth
import db
import styles
import widgets


class LoginClienteFrame(ttk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master, padding=30)
        self.on_login = on_login

        ttk.Label(self, text="🛒  Acceso de cliente", style="Section.TLabel", font=styles.FONT_HEADER).pack(
            pady=(0, 20)
        )

        tarjeta = ttk.Frame(self, style="Card.TFrame", padding=25)
        tarjeta.pack()

        notebook = ttk.Notebook(tarjeta)
        notebook.pack()

        tab_login = ttk.Frame(notebook, style="Card.TFrame", padding=20)
        tab_registro = ttk.Frame(notebook, style="Card.TFrame", padding=20)
        notebook.add(tab_login, text="Iniciar sesión")
        notebook.add(tab_registro, text="Crear cuenta")

        self._armar_tab_login(tab_login)
        self._armar_tab_registro(tab_registro)

        ttk.Button(
            self, text="← Volver", style="Ghost.TButton", command=lambda: self.master.event_generate("<<VolverInicio>>")
        ).pack(pady=20)

    def _armar_tab_login(self, tab):
        ttk.Label(tab, text="Usuario:", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.login_user_var = tk.StringVar()
        entry_user = ttk.Entry(tab, textvariable=self.login_user_var, width=30)
        entry_user.grid(row=1, column=0, pady=(0, 10))
        entry_user.focus()

        ttk.Label(tab, text="Contraseña:", style="Card.TLabel").grid(row=2, column=0, sticky="w")
        self.login_pass_var = tk.StringVar()
        entry_pass = ttk.Entry(tab, textvariable=self.login_pass_var, show="*", width=30)
        entry_pass.grid(row=3, column=0, pady=(0, 15))
        entry_pass.bind("<Return>", lambda e: self._login())

        ttk.Button(tab, text="Ingresar", style="Accent.TButton", command=self._login).grid(
            row=4, column=0, sticky="ew"
        )

    def _armar_tab_registro(self, tab):
        ttk.Label(tab, text="Correo registrado como cliente:", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.reg_email_var = tk.StringVar()
        ttk.Entry(tab, textvariable=self.reg_email_var, width=30).grid(row=1, column=0, pady=(0, 10))

        ttk.Label(tab, text="Nuevo usuario:", style="Card.TLabel").grid(row=2, column=0, sticky="w")
        self.reg_user_var = tk.StringVar()
        ttk.Entry(tab, textvariable=self.reg_user_var, width=30).grid(row=3, column=0, pady=(0, 10))

        ttk.Label(tab, text="Contraseña:", style="Card.TLabel").grid(row=4, column=0, sticky="w")
        self.reg_pass_var = tk.StringVar()
        ttk.Entry(tab, textvariable=self.reg_pass_var, show="*", width=30).grid(row=5, column=0, pady=(0, 10))

        ttk.Label(tab, text="Confirmar contraseña:", style="Card.TLabel").grid(row=6, column=0, sticky="w")
        self.reg_pass2_var = tk.StringVar()
        ttk.Entry(tab, textvariable=self.reg_pass2_var, show="*", width=30).grid(row=7, column=0, pady=(0, 15))

        ttk.Button(tab, text="Registrar", style="Accent.TButton", command=self._registrar).grid(
            row=8, column=0, sticky="ew"
        )

    def _login(self):
        username = self.login_user_var.get().strip()
        password = self.login_pass_var.get()
        if not username or not password:
            messagebox.showwarning("Faltan datos", "Escribe tu usuario y contraseña.")
            return

        rows = db.query("SELECT * FROM Usuario WHERE username = ? AND rol = 'cliente'", (username,))
        if not rows or not auth.verificar_password(password, rows[0]["salt"], rows[0]["password_hash"]):
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
            return

        cliente = db.query("SELECT * FROM Cliente WHERE id_cliente = ?", (rows[0]["id_cliente"],))[0]
        self.on_login(cliente)

    def _registrar(self):
        email = self.reg_email_var.get().strip()
        username = self.reg_user_var.get().strip()
        password = self.reg_pass_var.get()
        password2 = self.reg_pass2_var.get()

        if not email or not username or not password:
            messagebox.showwarning("Faltan datos", "Completa correo, usuario y contraseña.")
            return
        if password != password2:
            messagebox.showerror("Las contraseñas no coinciden", "Verifica la contraseña y su confirmación.")
            return
        if len(password) < 4:
            messagebox.showerror("Contraseña muy corta", "Usa al menos 4 caracteres.")
            return

        clientes = db.query("SELECT * FROM Cliente WHERE email = ?", (email,))
        if not clientes:
            messagebox.showerror(
                "Cliente no encontrado", "Ese correo no corresponde a ningún cliente registrado."
            )
            return
        id_cliente = clientes[0]["id_cliente"]

        if db.query("SELECT 1 FROM Usuario WHERE id_cliente = ?", (id_cliente,)):
            messagebox.showerror("Cuenta existente", "Este cliente ya tiene una cuenta creada.")
            return
        if db.query("SELECT 1 FROM Usuario WHERE username = ?", (username,)):
            messagebox.showerror("Usuario ocupado", "Ese nombre de usuario ya está en uso.")
            return

        salt = auth.generar_salt()
        password_hash = auth.hash_password(password, salt)
        db.execute(
            "INSERT INTO Usuario (username, password_hash, salt, rol, id_cliente) VALUES (?, ?, ?, 'cliente', ?)",
            (username, password_hash, salt, id_cliente),
        )
        messagebox.showinfo("Cuenta creada", "Tu cuenta se creó correctamente. Ya puedes iniciar sesión.")
        self.login_user_var.set(username)
        self.login_pass_var.set("")


class CatalogoFrame(ttk.Frame):
    def __init__(self, master, cliente):
        super().__init__(master, padding=0)
        self.cliente = cliente
        self.carrito = {}  # id_variante -> dict(info, cantidad)

        header = widgets.GradientBanner(self, styles.GRAD_TOP, styles.GRAD_BOTTOM, height=64)
        header.pack(fill="x")
        btn_cerrar = ttk.Button(
            header, text="Cerrar sesión", style="Accent.TButton",
            command=lambda: self.event_generate("<<VolverInicio>>"),
        )
        saludo = f"🛒 Hola, {cliente['nombre']} {cliente['apellido']}"

        def _hdr(_e=None):
            header.delete("hdr")
            header.create_text(
                22, 32, text=saludo, anchor="w", fill="white",
                font=("Segoe UI", 15, "bold"), tags="hdr",
            )
            header.coords(win_btn, header.winfo_width() - 22, 31)

        win_btn = header.create_window(0, 0, window=btn_cerrar, anchor="e")
        header.bind("<Configure>", lambda e: (header._redibujar(e), _hdr()), add="+")
        _hdr()

        cuerpo_general = ttk.Frame(self, padding=15)
        cuerpo_general.pack(fill="both", expand=True)
        self._cuerpo_general = cuerpo_general

        notebook = ttk.Notebook(cuerpo_general)
        notebook.pack(fill="both", expand=True)

        tab_comprar = ttk.Frame(notebook, padding=10)
        self.tab_pedidos = ttk.Frame(notebook, padding=10)
        notebook.add(tab_comprar, text="🛍️ Comprar")
        notebook.add(self.tab_pedidos, text="📦 Mis pedidos")

        filtros = ttk.Frame(tab_comprar)
        filtros.pack(fill="x", pady=(0, 10))

        ttk.Label(filtros, text="Tienda:").grid(row=0, column=0, sticky="w")
        self.almacen_var = tk.StringVar()
        self.almacen_combo = ttk.Combobox(filtros, textvariable=self.almacen_var, state="readonly", width=22)
        self.almacen_combo.grid(row=0, column=1, padx=5)
        self.almacen_combo.bind("<<ComboboxSelected>>", lambda e: self._cargar_catalogo())

        ttk.Label(filtros, text="Categoría:").grid(row=0, column=2, sticky="w")
        self.categoria_var = tk.StringVar()
        self.categoria_combo = ttk.Combobox(filtros, textvariable=self.categoria_var, state="readonly", width=16)
        self.categoria_combo.grid(row=0, column=3, padx=5)
        self.categoria_combo.bind("<<ComboboxSelected>>", lambda e: self._cargar_catalogo())

        ttk.Label(filtros, text="🔎 Buscar:").grid(row=0, column=4, sticky="w", padx=(10, 0))
        self.buscar_var = tk.StringVar()
        entry_buscar = ttk.Entry(filtros, textvariable=self.buscar_var, width=22)
        entry_buscar.grid(row=0, column=5, padx=5)
        entry_buscar.bind("<KeyRelease>", lambda e: self._buscar_con_retraso())
        self._debounce_id = None

        cuerpo = ttk.Frame(tab_comprar)
        cuerpo.pack(fill="both", expand=True)

        # ---- Galería de productos (grid de tarjetas) ----
        galeria_box = ttk.Frame(cuerpo)
        galeria_box.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.lbl_resultados = ttk.Label(galeria_box, text="", style="Muted.TLabel")
        self.lbl_resultados.pack(anchor="w", pady=(0, 6))

        self.galeria = widgets.ScrollableFrame(galeria_box)
        self.galeria.pack(fill="both", expand=True)
        self._num_columnas = 3
        self._pagina = 48          # productos por lote
        self._filas_catalogo = []  # resultado de la ultima consulta
        self._mostradas = 0        # cuantas tarjetas se han renderizado
        self._btn_mas = None

        # ---- Carrito (columna lateral) ----
        carrito_box = ttk.LabelFrame(cuerpo, text="🛒 Tu carrito")
        carrito_box.pack(side="left", fill="y")
        carrito_box.configure(width=340)

        col_carrito = ("producto", "cantidad", "subtotal")
        self.tree_carrito = ttk.Treeview(carrito_box, columns=col_carrito, show="headings", height=14)
        for col, ancho, titulo, anchor in [
            ("producto", 180, "Producto", "w"),
            ("cantidad", 55, "Cant.", "center"),
            ("subtotal", 85, "Subtotal", "e"),
        ]:
            self.tree_carrito.heading(col, text=titulo)
            self.tree_carrito.column(col, width=ancho, anchor=anchor)
        self.tree_carrito.pack(fill="both", expand=True, padx=6, pady=6)

        pie_carrito = ttk.Frame(carrito_box)
        pie_carrito.pack(fill="x", pady=5)
        ttk.Button(
            pie_carrito, text="Quitar", style="Ghost.TButton", command=self._quitar_del_carrito
        ).pack(side="left")
        self.total_var = tk.StringVar(value="Total: S/ 0.00")
        ttk.Label(pie_carrito, textvariable=self.total_var, style="Total.TLabel").pack(side="left", padx=15)
        ttk.Button(
            pie_carrito, text="Confirmar pedido ✓", style="Accent.TButton", command=self._confirmar_pedido
        ).pack(side="right")

        self._armar_tab_pedidos()
        self._cargar_filtros()

    def _armar_tab_pedidos(self):
        ttk.Button(
            self.tab_pedidos, text="↻ Actualizar", style="Ghost.TButton", command=self._cargar_mis_pedidos
        ).pack(anchor="w", pady=(0, 8))

        cols = ("id_pedido", "fecha", "estado", "total")
        self.tree_mis_pedidos = ttk.Treeview(self.tab_pedidos, columns=cols, show="headings", height=10)
        for col, ancho, titulo in [
            ("id_pedido", 80, "N° Pedido"),
            ("fecha", 150, "Fecha"),
            ("estado", 110, "Estado"),
            ("total", 100, "Total"),
        ]:
            self.tree_mis_pedidos.heading(col, text=titulo)
            self.tree_mis_pedidos.column(col, width=ancho)
        styles.hacer_ordenable(self.tree_mis_pedidos, cols)
        self.tree_mis_pedidos.pack(fill="both", expand=True)
        self.tree_mis_pedidos.bind("<<TreeviewSelect>>", self._al_seleccionar_mi_pedido)

        ttk.Label(
            self.tab_pedidos, text="Detalle del pedido seleccionado:", font=styles.FONT_BODY_BOLD
        ).pack(anchor="w", pady=(10, 4))
        cols_det = ("producto", "talla", "color", "cantidad", "precio", "subtotal")
        self.tree_mi_detalle = ttk.Treeview(self.tab_pedidos, columns=cols_det, show="headings", height=6)
        for col, ancho, titulo in [
            ("producto", 200, "Producto"),
            ("talla", 50, "Talla"),
            ("color", 70, "Color"),
            ("cantidad", 60, "Cant."),
            ("precio", 90, "Precio"),
            ("subtotal", 90, "Subtotal"),
        ]:
            self.tree_mi_detalle.heading(col, text=titulo)
            self.tree_mi_detalle.column(col, width=ancho)
        self.tree_mi_detalle.pack(fill="both", expand=True)

        self._cargar_mis_pedidos()

    def _cargar_mis_pedidos(self):
        self.tree_mis_pedidos.delete(*self.tree_mis_pedidos.get_children())
        self.tree_mi_detalle.delete(*self.tree_mi_detalle.get_children())
        sql = """
            SELECT id_pedido, fecha_compra, estado_pedido, total
            FROM Pedido
            WHERE id_cliente = ?
            ORDER BY fecha_compra DESC
        """
        filas = db.query(sql, (self.cliente["id_cliente"],))
        for r in filas:
            self.tree_mis_pedidos.insert(
                "",
                "end",
                iid=str(r["id_pedido"]),
                values=(
                    r["id_pedido"],
                    r["fecha_compra"].strftime("%d/%m/%Y %H:%M"),
                    r["estado_pedido"],
                    styles.moneda(r["total"]),
                ),
            )
        if not filas:
            styles.mostrar_vacio(self.tree_mis_pedidos, "Todavía no tienes pedidos registrados.")
        styles.zebra(self.tree_mis_pedidos)

    def _al_seleccionar_mi_pedido(self, _event):
        self.tree_mi_detalle.delete(*self.tree_mi_detalle.get_children())
        seleccion = self.tree_mis_pedidos.selection()
        if not seleccion or not seleccion[0].isdigit():
            return
        sql = """
            SELECT p.nombre AS producto, vp.talla, vp.color, dp.cantidad, dp.precio_unitario
            FROM Detalle_Pedido dp
            JOIN Variante_Producto vp ON dp.id_variante = vp.id_variante
            JOIN Producto p ON vp.id_producto = p.id_producto
            WHERE dp.id_pedido = ?
        """
        for r in db.query(sql, (int(seleccion[0]),)):
            subtotal = float(r["precio_unitario"]) * r["cantidad"]
            self.tree_mi_detalle.insert(
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
        styles.zebra(self.tree_mi_detalle)

    def _cargar_filtros(self):
        almacenes = db.query("SELECT id_almacen, nombre FROM Almacen ORDER BY nombre")
        self.almacenes_map = {a["nombre"]: a["id_almacen"] for a in almacenes}
        self.almacen_combo["values"] = list(self.almacenes_map.keys())
        if almacenes:
            self.almacen_combo.current(0)

        categorias = db.query("SELECT id_categoria, nombre FROM Categoria ORDER BY nombre")
        self.categorias_map = {c["nombre"]: c["id_categoria"] for c in categorias}
        self.categoria_combo["values"] = ["Todas"] + list(self.categorias_map.keys())
        self.categoria_combo.current(0)

        self._cargar_catalogo()

    def _buscar_con_retraso(self):
        """Debounce: espera a que el usuario deje de escribir antes de consultar."""
        if self._debounce_id is not None:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(350, self._cargar_catalogo)

    def _cargar_catalogo(self):
        self._debounce_id = None
        self.galeria.limpiar()
        self._btn_mas = None
        self._mostradas = 0
        self._id_almacen_actual = self.almacenes_map.get(self.almacen_var.get())
        if self._id_almacen_actual is None:
            return

        sql = """
            SELECT vp.id_variante, p.nombre AS producto, m.nombre AS marca,
                   c.nombre AS categoria, vp.talla, vp.color, vp.sku,
                   p.precio_base, i.cantidad_stock
            FROM Inventario i
            JOIN Variante_Producto vp ON i.id_variante = vp.id_variante
            JOIN Producto p ON vp.id_producto = p.id_producto
            JOIN Marca m ON p.id_marca = m.id_marca
            JOIN Categoria c ON p.id_categoria = c.id_categoria
            WHERE i.id_almacen = ? AND i.cantidad_stock > 0
        """
        params = [self._id_almacen_actual]
        categoria_sel = self.categoria_var.get()
        if categoria_sel and categoria_sel != "Todas":
            sql += " AND p.id_categoria = ?"
            params.append(self.categorias_map[categoria_sel])
        texto = self.buscar_var.get().strip()
        if texto:
            sql += " AND p.nombre LIKE ?"
            params.append(f"%{texto}%")
        sql += " ORDER BY p.nombre, vp.talla, vp.color"

        self._filas_catalogo = db.query(sql, tuple(params))
        total = len(self._filas_catalogo)
        self.lbl_resultados.configure(text=f"{total} productos disponibles")

        if not total:
            tk.Label(
                self.galeria.interior,
                text="😕  No se encontraron productos con ese filtro.",
                bg=styles.COLOR_BG, fg=styles.COLOR_MUTED, font=("Segoe UI", 11),
            ).pack(pady=40)
            return

        for i in range(self._num_columnas):
            self.galeria.interior.columnconfigure(i, weight=1)
        self._renderizar_lote()

    def _renderizar_lote(self):
        """Renderiza el siguiente lote de tarjetas (paginación)."""
        if self._btn_mas is not None:
            self._btn_mas.destroy()
            self._btn_mas = None

        cols = self._num_columnas
        fin = min(self._mostradas + self._pagina, len(self._filas_catalogo))
        for idx in range(self._mostradas, fin):
            r = self._filas_catalogo[idx]
            producto = {
                "id_variante": r["id_variante"],
                "nombre": r["producto"],
                "marca": r["marca"],
                "categoria": r["categoria"],
                "talla": r["talla"],
                "color": r["color"],
                "precio": float(r["precio_base"]),
                "stock": r["cantidad_stock"],
                "id_almacen": self._id_almacen_actual,
            }
            card = widgets.ProductCard(self.galeria.interior, producto, on_add=self._agregar_carrito)
            card.grid(row=idx // cols, column=idx % cols, padx=8, pady=8)
        self._mostradas = fin

        restantes = len(self._filas_catalogo) - self._mostradas
        if restantes > 0:
            self._btn_mas = ttk.Button(
                self.galeria.interior,
                text=f"▾  Mostrar más ({restantes} restantes)",
                style="Secondary.TButton", command=self._renderizar_lote,
            )
            self._btn_mas.grid(row=(fin - 1) // cols + 1, column=0, columnspan=cols, pady=14)

    def _agregar_carrito(self, producto):
        id_variante = producto["id_variante"]
        ya_en_carrito = self.carrito.get(id_variante, {}).get("cantidad", 0)
        if ya_en_carrito + 1 > producto["stock"]:
            messagebox.showwarning(
                "Stock insuficiente", f"Solo hay {producto['stock']} unidades disponibles de este producto."
            )
            return

        if id_variante in self.carrito:
            self.carrito[id_variante]["cantidad"] += 1
        else:
            self.carrito[id_variante] = {
                "producto": producto["nombre"],
                "talla": producto["talla"],
                "color": producto["color"],
                "precio": producto["precio"],
                "cantidad": 1,
                "id_almacen": producto["id_almacen"],
            }
        self._refrescar_carrito()

    def _quitar_del_carrito(self):
        seleccion = self.tree_carrito.selection()
        if not seleccion or not seleccion[0].isdigit():
            return
        id_variante = int(seleccion[0])
        del self.carrito[id_variante]
        self._refrescar_carrito()

    def _refrescar_carrito(self):
        for row in self.tree_carrito.get_children():
            self.tree_carrito.delete(row)
        total = 0.0
        for id_variante, item in self.carrito.items():
            subtotal = item["precio"] * item["cantidad"]
            total += subtotal
            nombre_corto = f"{item['producto']}  ({item['talla']}/{item['color']})"
            self.tree_carrito.insert(
                "",
                "end",
                iid=str(id_variante),
                values=(
                    nombre_corto,
                    item["cantidad"],
                    styles.moneda(subtotal),
                ),
            )
        if not self.carrito:
            styles.mostrar_vacio(self.tree_carrito, "Tu carrito está vacío.")
        styles.zebra(self.tree_carrito)
        self.total_var.set(f"Total: {styles.moneda(total)}")

    def _confirmar_pedido(self):
        if not self.carrito:
            messagebox.showinfo("Carrito vacío", "Agrega al menos un producto antes de confirmar.")
            return

        conn = db.get_connection()
        try:
            cur = conn.cursor()
            total = sum(item["precio"] * item["cantidad"] for item in self.carrito.values())

            cur.execute(
                "INSERT INTO Pedido (id_cliente, fecha_compra, estado_pedido, total) "
                "OUTPUT INSERTED.id_pedido VALUES (?, GETDATE(), 'Pagado', ?)",
                (self.cliente["id_cliente"], total),
            )
            id_pedido = cur.fetchone()[0]

            for id_variante, item in self.carrito.items():
                cur.execute(
                    "SELECT cantidad_stock FROM Inventario WHERE id_variante = ? AND id_almacen = ?",
                    (id_variante, item["id_almacen"]),
                )
                stock_actual = cur.fetchone()[0]
                if stock_actual < item["cantidad"]:
                    conn.rollback()
                    messagebox.showerror(
                        "Stock insuficiente",
                        f"El stock de {item['producto']} cambió. Vuelve a revisar el catálogo.",
                    )
                    self._cargar_catalogo()
                    return

                cur.execute(
                    "INSERT INTO Detalle_Pedido (id_pedido, id_variante, cantidad, precio_unitario) "
                    "VALUES (?, ?, ?, ?)",
                    (id_pedido, id_variante, item["cantidad"], item["precio"]),
                )
                cur.execute(
                    "UPDATE Inventario SET cantidad_stock = cantidad_stock - ?, "
                    "fecha_ultima_actualizacion = GETDATE() WHERE id_variante = ? AND id_almacen = ?",
                    (item["cantidad"], id_variante, item["id_almacen"]),
                )

            conn.commit()
            messagebox.showinfo(
                "Pedido confirmado", f"Pedido #{id_pedido} registrado. Total: {styles.moneda(total)}"
            )
            self.carrito.clear()
            self._refrescar_carrito()
            self._cargar_catalogo()
            self._cargar_mis_pedidos()
        except Exception as exc:
            conn.rollback()
            messagebox.showerror("Error al confirmar el pedido", str(exc))
        finally:
            conn.close()
