import tkinter as tk
from tkinter import ttk, messagebox

import db
import styles

ESTADOS_COMPRA = ["Pendiente", "Enviado", "Entregado", "Recibida"]


class ProveedoresTab(ttk.Frame):
    """Gestión de proveedores: ver, buscar, agregar y editar."""

    def __init__(self, master):
        super().__init__(master, style="Card.TFrame", padding=15)
        self._id_sel = None

        buscar_box = ttk.Frame(self, style="Card.TFrame")
        buscar_box.pack(fill="x", pady=(0, 8))
        ttk.Label(buscar_box, text="🔎 Buscar proveedor:", style="Card.TLabel").pack(side="left")
        self.buscar_var = tk.StringVar()
        e = ttk.Entry(buscar_box, textvariable=self.buscar_var, width=30)
        e.pack(side="left", padx=5)
        e.bind("<KeyRelease>", lambda ev: self._cargar())

        cols = ("id", "razon", "ruc", "contacto", "telefono", "email")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=11)
        for c, ancho, titulo in [
            ("id", 40, "ID"),
            ("razon", 220, "Razón social"),
            ("ruc", 110, "RUC / Doc."),
            ("contacto", 140, "Contacto"),
            ("telefono", 90, "Teléfono"),
            ("email", 200, "Email"),
        ]:
            self.tree.heading(c, text=titulo)
            self.tree.column(c, width=ancho)
        styles.hacer_ordenable(self.tree, cols)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._al_seleccionar)

        # formulario
        form = ttk.LabelFrame(self, text="Datos del proveedor")
        form.pack(fill="x", pady=(10, 0))
        self.vars = {k: tk.StringVar() for k in ("razon", "ruc", "contacto", "telefono", "email")}
        campos = [
            ("Razón social:", "razon", 34),
            ("RUC / Doc.:", "ruc", 16),
            ("Contacto:", "contacto", 22),
            ("Teléfono:", "telefono", 14),
            ("Email:", "email", 26),
        ]
        fila = ttk.Frame(form)
        fila.pack(fill="x", padx=8, pady=8)
        for i, (etq, key, ancho) in enumerate(campos):
            col = ttk.Frame(fila)
            col.grid(row=0, column=i, padx=4, sticky="w")
            ttk.Label(col, text=etq).pack(anchor="w")
            ttk.Entry(col, textvariable=self.vars[key], width=ancho).pack()

        botones = ttk.Frame(form)
        botones.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(botones, text="Guardar", style="Accent.TButton", command=self._guardar).pack(side="left", padx=3)
        ttk.Button(botones, text="Nuevo / Limpiar", style="Ghost.TButton", command=self._limpiar).pack(side="left", padx=3)

        self._cargar()

    def _cargar(self):
        self.tree.delete(*self.tree.get_children())
        sql = "SELECT id_proveedor, razon_social, ruc_o_documento, nombre_contacto, telefono, email FROM Proveedor WHERE 1=1"
        params = []
        texto = self.buscar_var.get().strip()
        if texto:
            sql += " AND (razon_social LIKE ? OR ruc_o_documento LIKE ?)"
            params += [f"%{texto}%", f"%{texto}%"]
        sql += " ORDER BY razon_social"
        filas = db.query(sql, tuple(params))
        for r in filas:
            self.tree.insert(
                "", "end", iid=str(r["id_proveedor"]),
                values=(r["id_proveedor"], r["razon_social"], r["ruc_o_documento"],
                        r["nombre_contacto"], r["telefono"], r["email"]),
            )
        if not filas:
            styles.mostrar_vacio(self.tree, "No se encontraron proveedores.")
        styles.zebra(self.tree)

    def _al_seleccionar(self, _e):
        sel = self.tree.selection()
        if not sel or not sel[0].isdigit():
            return
        v = self.tree.item(sel[0], "values")
        self._id_sel = int(v[0])
        self.vars["razon"].set(v[1])
        self.vars["ruc"].set(v[2])
        self.vars["contacto"].set(v[3])
        self.vars["telefono"].set(v[4])
        self.vars["email"].set(v[5])

    def _limpiar(self):
        self._id_sel = None
        for v in self.vars.values():
            v.set("")
        self.tree.selection_remove(self.tree.selection())

    def _guardar(self):
        razon = self.vars["razon"].get().strip()
        if not razon:
            messagebox.showwarning("Falta la razón social", "La razón social es obligatoria.")
            return
        datos = (
            razon, self.vars["ruc"].get().strip(), self.vars["contacto"].get().strip(),
            self.vars["telefono"].get().strip(), self.vars["email"].get().strip(),
        )
        if self._id_sel is None:
            db.execute(
                "INSERT INTO Proveedor (razon_social, ruc_o_documento, nombre_contacto, telefono, email) "
                "VALUES (?, ?, ?, ?, ?)", datos,
            )
            messagebox.showinfo("Proveedor agregado", "El proveedor se registró correctamente.")
        else:
            db.execute(
                "UPDATE Proveedor SET razon_social=?, ruc_o_documento=?, nombre_contacto=?, telefono=?, email=? "
                "WHERE id_proveedor=?", (*datos, self._id_sel),
            )
            messagebox.showinfo("Proveedor actualizado", "Los datos se guardaron correctamente.")
        self._limpiar()
        self._cargar()


class ComprasTab(ttk.Frame):
    """Órdenes de compra: ver, crear y recibir (suma stock al inventario)."""

    def __init__(self, master, on_stock_cambiado=None):
        super().__init__(master, style="Card.TFrame", padding=15)
        self._on_stock_cambiado = on_stock_cambiado

        barra = ttk.Frame(self, style="Card.TFrame")
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Estado:", style="Card.TLabel").pack(side="left")
        self.filtro_estado = tk.StringVar(value="Todos")
        combo = ttk.Combobox(barra, textvariable=self.filtro_estado, values=["Todos"] + ESTADOS_COMPRA,
                             state="readonly", width=14)
        combo.pack(side="left", padx=5)
        combo.bind("<<ComboboxSelected>>", lambda e: self._cargar())
        ttk.Button(barra, text="＋ Nueva orden", style="Accent.TButton", command=self._nueva_orden).pack(side="right", padx=3)
        ttk.Button(barra, text="📦 Recibir orden", style="Secondary.TButton", command=self._recibir_orden).pack(side="right", padx=3)

        cols = ("id", "proveedor", "fecha", "estado", "costo")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=9)
        for c, ancho, titulo in [
            ("id", 60, "N° Orden"),
            ("proveedor", 240, "Proveedor"),
            ("fecha", 130, "Fecha emisión"),
            ("estado", 100, "Estado"),
            ("costo", 110, "Costo total"),
        ]:
            self.tree.heading(c, text=titulo)
            self.tree.column(c, width=ancho)
        styles.hacer_ordenable(self.tree, cols)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._al_seleccionar)

        ttk.Label(self, text="Detalle de la orden:", style="Card.TLabel", font=styles.FONT_BODY_BOLD).pack(
            anchor="w", pady=(10, 4)
        )
        cols_det = ("producto", "sku", "cantidad", "costo_u", "subtotal")
        self.tree_det = ttk.Treeview(self, columns=cols_det, show="headings", height=6)
        for c, ancho, titulo in [
            ("producto", 220, "Producto"),
            ("sku", 140, "SKU"),
            ("cantidad", 70, "Cantidad"),
            ("costo_u", 90, "Costo unit."),
            ("subtotal", 100, "Subtotal"),
        ]:
            self.tree_det.heading(c, text=titulo)
            self.tree_det.column(c, width=ancho)
        self.tree_det.pack(fill="both", expand=True)

        self._cargar()

    def _cargar(self):
        self.tree.delete(*self.tree.get_children())
        self.tree_det.delete(*self.tree_det.get_children())
        sql = """
            SELECT oc.id_orden_compra, p.razon_social, oc.fecha_emision, oc.estado, oc.costo_total
            FROM Orden_Compra oc
            JOIN Proveedor p ON oc.id_proveedor = p.id_proveedor
            WHERE 1=1
        """
        params = []
        estado = self.filtro_estado.get()
        if estado and estado != "Todos":
            sql += " AND oc.estado = ?"
            params.append(estado)
        sql += " ORDER BY oc.fecha_emision DESC"
        filas = db.query(sql, tuple(params))
        for r in filas:
            self.tree.insert(
                "", "end", iid=str(r["id_orden_compra"]),
                values=(r["id_orden_compra"], r["razon_social"],
                        r["fecha_emision"].strftime("%d/%m/%Y"), r["estado"], styles.moneda(r["costo_total"])),
            )
        if not filas:
            styles.mostrar_vacio(self.tree, "No hay órdenes de compra con ese filtro.")
        styles.zebra(self.tree)

    def _al_seleccionar(self, _e):
        self.tree_det.delete(*self.tree_det.get_children())
        sel = self.tree.selection()
        if not sel or not sel[0].isdigit():
            return
        sql = """
            SELECT p.nombre AS producto, vp.sku, dc.cantidad, dc.costo_unitario
            FROM Detalle_Compra dc
            JOIN Variante_Producto vp ON dc.id_variante = vp.id_variante
            JOIN Producto p ON vp.id_producto = p.id_producto
            WHERE dc.id_orden_compra = ?
        """
        for r in db.query(sql, (int(sel[0]),)):
            subtotal = float(r["costo_unitario"]) * r["cantidad"]
            self.tree_det.insert(
                "", "end",
                values=(r["producto"], r["sku"], r["cantidad"],
                        styles.moneda(r["costo_unitario"]), styles.moneda(subtotal)),
            )
        styles.zebra(self.tree_det)

    def _recibir_orden(self):
        sel = self.tree.selection()
        if not sel or not sel[0].isdigit():
            messagebox.showinfo("Selecciona una orden", "Elige una orden de compra de la lista.")
            return
        id_orden = int(sel[0])
        estado = self.tree.item(sel[0], "values")[3]
        if estado == "Recibida":
            messagebox.showinfo("Orden ya recibida", "Esta orden ya fue recibida en el inventario.")
            return

        almacenes = db.query("SELECT id_almacen, nombre FROM Almacen ORDER BY nombre")
        dlg = _DialogoRecibir(self, almacenes)
        self.wait_window(dlg)
        if dlg.id_almacen is None:
            return

        conn = db.get_connection()
        try:
            cur = conn.cursor()
            lineas = db.query(
                "SELECT id_variante, cantidad FROM Detalle_Compra WHERE id_orden_compra = ?", (id_orden,)
            )
            for ln in lineas:
                cur.execute(
                    "SELECT id_inventario FROM Inventario WHERE id_variante = ? AND id_almacen = ?",
                    (ln["id_variante"], dlg.id_almacen),
                )
                row = cur.fetchone()
                if row:
                    cur.execute(
                        "UPDATE Inventario SET cantidad_stock = cantidad_stock + ?, "
                        "fecha_ultima_actualizacion = GETDATE() WHERE id_inventario = ?",
                        (ln["cantidad"], row[0]),
                    )
                else:
                    cur.execute(
                        "INSERT INTO Inventario (id_variante, id_almacen, cantidad_stock, fecha_ultima_actualizacion) "
                        "VALUES (?, ?, ?, GETDATE())",
                        (ln["id_variante"], dlg.id_almacen, ln["cantidad"]),
                    )
            cur.execute("UPDATE Orden_Compra SET estado = 'Recibida' WHERE id_orden_compra = ?", (id_orden,))
            conn.commit()
            messagebox.showinfo("Orden recibida", f"El stock de la orden #{id_orden} se sumó al inventario.")
            self._cargar()
            if self._on_stock_cambiado:
                self._on_stock_cambiado()
        except Exception as exc:
            conn.rollback()
            messagebox.showerror("Error al recibir la orden", str(exc))
        finally:
            conn.close()

    def _nueva_orden(self):
        dlg = _DialogoNuevaOrden(self)
        self.wait_window(dlg)
        if dlg.creada:
            self._cargar()


class _DialogoRecibir(tk.Toplevel):
    def __init__(self, master, almacenes):
        super().__init__(master)
        self.title("Recibir orden en almacén")
        self.configure(bg=styles.COLOR_BG)
        self.id_almacen = None
        self._mapa = {a["nombre"]: a["id_almacen"] for a in almacenes}

        ttk.Label(self, text="¿En qué almacén se recibe la mercadería?", padding=15).pack()
        self.var = tk.StringVar()
        combo = ttk.Combobox(self, textvariable=self.var, values=list(self._mapa.keys()), state="readonly", width=30)
        combo.pack(padx=15)
        if almacenes:
            combo.current(0)
        btns = ttk.Frame(self, padding=15)
        btns.pack()
        ttk.Button(btns, text="Recibir", style="Accent.TButton", command=self._ok).pack(side="left", padx=5)
        ttk.Button(btns, text="Cancelar", style="Ghost.TButton", command=self.destroy).pack(side="left", padx=5)
        self.transient(master)
        self.grab_set()

    def _ok(self):
        self.id_almacen = self._mapa.get(self.var.get())
        self.destroy()


class _DialogoNuevaOrden(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Nueva orden de compra")
        self.geometry("640x520")
        self.configure(bg=styles.COLOR_BG)
        self.creada = False
        self._lineas = []  # (id_variante, etiqueta, cantidad, costo)

        cont = ttk.Frame(self, padding=15)
        cont.pack(fill="both", expand=True)

        ttk.Label(cont, text="Proveedor:").grid(row=0, column=0, sticky="w")
        self._prov = db.query("SELECT id_proveedor, razon_social FROM Proveedor ORDER BY razon_social")
        self._prov_map = {p["razon_social"]: p["id_proveedor"] for p in self._prov}
        self.prov_var = tk.StringVar()
        cb_prov = ttk.Combobox(cont, textvariable=self.prov_var, values=list(self._prov_map.keys()),
                               state="readonly", width=44)
        cb_prov.grid(row=0, column=1, columnspan=3, sticky="w", pady=4)
        if self._prov:
            cb_prov.current(0)

        ttk.Separator(cont, orient="horizontal").grid(row=1, column=0, columnspan=4, sticky="ew", pady=8)

        ttk.Label(cont, text="Producto (SKU):").grid(row=2, column=0, sticky="w")
        self._vars = db.query(
            """
            SELECT vp.id_variante, p.nombre + ' — ' + vp.sku AS etiqueta, p.precio_base
            FROM Variante_Producto vp JOIN Producto p ON vp.id_producto = p.id_producto
            ORDER BY p.nombre
            """
        )
        self._var_map = {v["etiqueta"]: v for v in self._vars}
        self.var_sel = tk.StringVar()
        cb = ttk.Combobox(cont, textvariable=self.var_sel, values=list(self._var_map.keys()), width=44)
        cb.grid(row=2, column=1, columnspan=3, sticky="w", pady=4)

        ttk.Label(cont, text="Cantidad:").grid(row=3, column=0, sticky="w")
        self.cant_var = tk.IntVar(value=10)
        ttk.Spinbox(cont, from_=1, to=999, textvariable=self.cant_var, width=8).grid(row=3, column=1, sticky="w")
        ttk.Label(cont, text="Costo unitario:").grid(row=3, column=2, sticky="e")
        self.costo_var = tk.StringVar()
        ttk.Entry(cont, textvariable=self.costo_var, width=10).grid(row=3, column=3, sticky="w")
        ttk.Button(cont, text="Agregar línea", style="Ghost.TButton", command=self._agregar_linea).grid(
            row=4, column=1, sticky="w", pady=6
        )

        self.tree = ttk.Treeview(cont, columns=("prod", "cant", "costo", "sub"), show="headings", height=8)
        for c, ancho, t in [("prod", 300, "Producto"), ("cant", 70, "Cant."), ("costo", 90, "Costo u."), ("sub", 90, "Subtotal")]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=ancho)
        self.tree.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=6)
        cont.rowconfigure(5, weight=1)

        self.total_lbl = ttk.Label(cont, text="Total: S/ 0.00", style="Total.TLabel")
        self.total_lbl.grid(row=6, column=0, columnspan=2, sticky="w")
        btns = ttk.Frame(cont)
        btns.grid(row=6, column=2, columnspan=2, sticky="e")
        ttk.Button(btns, text="Guardar orden", style="Accent.TButton", command=self._guardar).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancelar", style="Ghost.TButton", command=self.destroy).pack(side="left", padx=4)

        self.transient(master)
        self.grab_set()

    def _agregar_linea(self):
        etq = self.var_sel.get().strip()
        if etq not in self._var_map:
            messagebox.showinfo("Selecciona un producto", "Elige un producto válido de la lista.", parent=self)
            return
        var = self._var_map[etq]
        try:
            costo = float(self.costo_var.get()) if self.costo_var.get().strip() else round(float(var["precio_base"]) * 0.6, 2)
            cant = int(self.cant_var.get())
            if costo < 0 or cant <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Datos inválidos", "Cantidad y costo deben ser números válidos.", parent=self)
            return
        self._lineas.append((var["id_variante"], etq, cant, costo))
        self._refrescar()

    def _refrescar(self):
        self.tree.delete(*self.tree.get_children())
        total = 0.0
        for _idv, etq, cant, costo in self._lineas:
            sub = cant * costo
            total += sub
            self.tree.insert("", "end", values=(etq, cant, styles.moneda(costo), styles.moneda(sub)))
        self.total_lbl.configure(text=f"Total: {styles.moneda(total)}")

    def _guardar(self):
        if self.prov_var.get() not in self._prov_map:
            messagebox.showwarning("Falta el proveedor", "Selecciona un proveedor.", parent=self)
            return
        if not self._lineas:
            messagebox.showwarning("Sin líneas", "Agrega al menos un producto a la orden.", parent=self)
            return
        id_prov = self._prov_map[self.prov_var.get()]
        total = sum(c * co for _i, _e, c, co in self._lineas)

        conn = db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO Orden_Compra (id_proveedor, fecha_emision, estado, costo_total) "
                "OUTPUT INSERTED.id_orden_compra VALUES (?, GETDATE(), 'Pendiente', ?)",
                (id_prov, total),
            )
            id_orden = cur.fetchone()[0]
            for id_var, _etq, cant, costo in self._lineas:
                cur.execute(
                    "INSERT INTO Detalle_Compra (id_orden_compra, id_variante, cantidad, costo_unitario) "
                    "VALUES (?, ?, ?, ?)", (id_orden, id_var, cant, costo),
                )
            conn.commit()
            self.creada = True
            messagebox.showinfo("Orden creada", f"Orden de compra #{id_orden} registrada como 'Pendiente'.", parent=self)
            self.destroy()
        except Exception as exc:
            conn.rollback()
            messagebox.showerror("Error al guardar la orden", str(exc), parent=self)
        finally:
            conn.close()
