import random
from datetime import datetime, timedelta
import os

def main():
    # Semilla para que sea reproducible
    random.seed(42)
    
    sql_lines = []
    
    # Cabecera SQL
    sql_lines.append("USE [Tienda_Total_Sport];")
    sql_lines.append("GO\n")
    
    # Desactivar restricciones temporalmente si es necesario, o insertar en orden jerárquico.
    # Usaremos SET IDENTITY_INSERT para poder insertar claves primarias exactas y asegurar relaciones.
    
    # 1. ALMACENES
    almacenes = [
        (1, "Almacén Central - Lima", "Av. Javier Prado Este 1234, San Isidro, Lima"),
        (2, "Almacén Norte - Trujillo", "Av. Larco 456, Trujillo"),
        (3, "Almacén Sur - Arequipa", "Calle Mercaderes 789, Arequipa")
    ]
    
    sql_lines.append("PRINT 'Insertando Almacenes...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Almacen] ON;")
    for id_a, nom, dir_a in almacenes:
        sql_lines.append(f"INSERT INTO [dbo].[Almacen] (id_almacen, nombre, direccion) VALUES ({id_a}, '{nom}', '{dir_a}');")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Almacen] OFF;")
    sql_lines.append("GO\n")
    
    # 2. MARCAS
    marcas = [
        (1, "Nike"),
        (2, "Adidas"),
        (3, "Puma"),
        (4, "Under Armour"),
        (5, "Reebok"),
        (6, "Asics")
    ]
    sql_lines.append("PRINT 'Insertando Marcas...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Marca] ON;")
    for id_m, nom in marcas:
        sql_lines.append(f"INSERT INTO [dbo].[Marca] (id_marca, nombre) VALUES ({id_m}, '{nom}');")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Marca] OFF;")
    sql_lines.append("GO\n")
    
    # 3. CATEGORIAS
    categorias = [
        (1, "Zapatillas", "Numérico"),
        (2, "Camisetas", "Letra"),
        (3, "Pantalones", "Letra"),
        (4, "Shorts", "Letra"),
        (5, "Casacas", "Letra"),
        (6, "Accesorios", "Única")
    ]
    sql_lines.append("PRINT 'Insertando Categorías...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Categoria] ON;")
    for id_c, nom, talla in categorias:
        sql_lines.append(f"INSERT INTO [dbo].[Categoria] (id_categoria, nombre, tipo_talla) VALUES ({id_c}, '{nom}', '{talla}');")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Categoria] OFF;")
    sql_lines.append("GO\n")
    
    # 4. PRODUCTOS (100 productos)
    # Generar combinaciones de nombres coherentes por categoría
    nombres_por_categoria = {
        1: ["Air Max", "Pegasus", "Ultraboost", "Superstar", "Rider", "Cali", "Charged Assert", "Project Rock", "Nano X", "Club C", "Gel-Kayano", "Nimbus"],
        2: ["Camiseta Dry-Fit", "Polo AeroReady", "Camiseta Active", "Polo Tech", "Camiseta Workout", "Polo Classic Sport"],
        3: ["Pantalon Essential", "Jogger Sportswear", "Pantalon Training", "Jogger Fleece", "Pantalon Track", "Pantalon Run"],
        4: ["Short Pro", "Short Flex", "Short Run", "Short Training", "Short Mesh", "Short Elite"],
        5: ["Casaca Windrunner", "Casaca Terrex", "Casaca Windbreaker", "Casaca Rain Jacket", "Casaca Fleece Hooded"],
        6: ["Medias Cushion (Pack 3)", "Gorra Heritage", "Mochila Classic", "Muñequeras Pro", "Cangurera Sport"]
    }
    
    generos = ["Hombre", "Mujer", "Unisex"]
    
    productos = []
    prod_counter = 1
    
    # Generamos 100 productos
    while prod_counter <= 100:
        cat_id, cat_nom, _ = random.choice(categorias)
        marca_id, marca_nom = random.choice(marcas)
        modelo = random.choice(nombres_por_categoria[cat_id])
        genero = random.choice(generos)
        
        # Nombre compuesto para evitar duplicados exactos
        variaciones_nombre = ["Pro", "Elite", "Run", "Training", "Essential", "Classic", "V2", "Speed", "Comfort", "Retro"]
        var_nom = random.choice(variaciones_nombre)
        nombre_prod = f"{cat_nom[:-1] if cat_nom.endswith('s') and cat_id != 6 else cat_nom} {marca_nom} {modelo} {var_nom}"
        
        # Evitar nombres duplicados
        if any(p[3] == nombre_prod for p in productos):
            continue
            
        precio_base = round(random.uniform(50.0, 350.0) if cat_id == 1 else random.uniform(15.0, 120.0), 2)
        desc = f"Excelente {nombre_prod.lower()} diseñado para maximizar el rendimiento deportivo y garantizar la comodidad durante entrenamientos intensos."
        
        productos.append((prod_counter, marca_id, cat_id, nombre_prod, desc, genero, precio_base))
        prod_counter += 1
        
    sql_lines.append("PRINT 'Insertando Productos...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Producto] ON;")
    for id_p, id_m, id_c, nom, desc, gen, prec in productos:
        desc_esc = desc.replace("'", "''")
        nom_esc = nom.replace("'", "''")
        sql_lines.append(f"INSERT INTO [dbo].[Producto] (id_producto, id_marca, id_categoria, nombre, descripcion, genero, precio_base) VALUES ({id_p}, {id_m}, {id_c}, '{nom_esc}', '{desc_esc}', '{gen}', {prec});")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Producto] OFF;")
    sql_lines.append("GO\n")
    
    # 5. VARIANTES DE PRODUCTO
    variantes = []
    var_counter = 1
    
    colores = ["Rojo", "Azul", "Negro", "Blanco", "Gris", "Plomo", "Verde", "Naranja"]
    tallas_calzado = ["38", "39", "40", "41", "42", "43"]
    tallas_ropa = ["S", "M", "L", "XL"]
    tallas_accesorios = ["Estándar"]
    
    sql_lines.append("PRINT 'Insertando Variantes de Producto...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Variante_Producto] ON;")
    for id_p, id_m, id_c, nom, _, _, _ in productos:
        if id_c == 1:
            tallas_pool = tallas_calzado
        elif id_c == 6:
            tallas_pool = tallas_accesorios
        else:
            tallas_pool = tallas_ropa
            
        num_variantes = random.randint(2, 3)
        tallas_seleccionadas = random.sample(tallas_pool, min(num_variantes, len(tallas_pool)))
        
        for talla in tallas_seleccionadas:
            color = random.choice(colores)
            marca_abbr = nom.split()[1][:3].upper()
            talla_abbr = talla.replace("á", "a").replace("é", "e")
            color_abbr = color[:3].upper()
            sku = f"TTS-{id_p:03d}-{id_c}{marca_abbr}-{talla_abbr}-{color_abbr}"
            
            variantes.append((var_counter, id_p, talla, color, sku))
            sql_lines.append(f"INSERT INTO [dbo].[Variante_Producto] (id_variante, id_producto, talla, color, sku) VALUES ({var_counter}, {id_p}, '{talla}', '{color}', '{sku}');")
            var_counter += 1
            
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Variante_Producto] OFF;")
    sql_lines.append("GO\n")
    
    # 6. INVENTARIO
    sql_lines.append("PRINT 'Insertando Inventario...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Inventario] ON;")
    inv_counter = 1
    for var in variantes:
        id_var = var[0]
        almacenes_elegidos = random.sample(almacenes, random.randint(1, 3))
        for id_a, _, _ in almacenes_elegidos:
            stock = random.randint(5, 50)
            fecha_act = datetime.now() - timedelta(days=random.randint(0, 30))
            fecha_str = fecha_act.strftime("%Y-%m-%d %H:%M:%S")
            sql_lines.append(f"INSERT INTO [dbo].[Inventario] (id_inventario, id_variante, id_almacen, cantidad_stock, fecha_ultima_actualizacion) VALUES ({inv_counter}, {id_var}, {id_a}, {stock}, '{fecha_str}');")
            inv_counter += 1
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Inventario] OFF;")
    sql_lines.append("GO\n")
    
    # 7. CLIENTES (200 clientes)
    nombres_m = ["Juan", "Carlos", "Luis", "Jorge", "Miguel", "Andres", "Jose", "Pedro", "David", "Francisco", "Manuel", "Alejandro", "Christian", "Roberto", "Daniel", "Oscar", "Javier", "Hugo", "Mario", "Fernando"]
    nombres_f = ["Maria", "Ana", "Luisa", "Carmen", "Sofia", "Laura", "Elena", "Isabel", "Lucia", "Paula", "Andrea", "Camila", "Valeria", "Gabriela", "Patricia", "Rosa", "Marta", "Julia", "Beatriz", "Silvia"]
    apellidos = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Gomez", "Martin", "Jimenez", "Ruiz", "Hernandez", "Diaz", "Moreno", "Muñoz", "Alvarez", "Romero", "Alonso", "Gutierrez", "Torres", "Salazar", "Rojas", "Flores", "Castillo", "Vargas", "Mendoza", "Caceres", "Campos", "Medina"]
    
    dominios = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]
    distritos = ["San Isidro", "Miraflores", "Surco", "San Borja", "La Molina", "San Miguel", "Jesús María", "Lince", "Pueblo Libre", "Magdalena", "Chorrillos", "Barranco"]
    
    clientes = []
    sql_lines.append("PRINT 'Insertando Clientes...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Cliente] ON;")
    
    for i in range(1, 201):
        genero = random.choice(["M", "F"])
        nombre = random.choice(nombres_m) if genero == "M" else random.choice(nombres_f)
        apellido_p = random.choice(apellidos)
        apellido_m = random.choice(apellidos)
        apellido = f"{apellido_p} {apellido_m}"
        
        email = f"{nombre.lower()}.{apellido_p.lower()}{i:03d}@{random.choice(dominios)}"
        telefono = f"9{random.randint(10000000, 99999999)}"
        direccion = f"Av. Los Precursores {random.randint(100, 1500)}, {random.choice(distritos)}, Lima"
        
        fecha_reg = datetime.now() - timedelta(days=random.randint(5, 365))
        fecha_str = fecha_reg.strftime("%Y-%m-%d %H:%M:%S")
        
        clientes.append((i, nombre, apellido, email, telefono, direccion, fecha_reg))
        sql_lines.append(f"INSERT INTO [dbo].[Cliente] (id_cliente, nombre, apellido, email, telefono, direccion, fecha_registro) VALUES ({i}, '{nombre}', '{apellido}', '{email}', '{telefono}', '{direccion}', '{fecha_str}');")
        
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Cliente] OFF;")
    sql_lines.append("GO\n")
    
    # 8. PROVEEDORES (10 proveedores)
    proveedores_data = [
        ("Distribuidora Sport Perú S.A.C.", "20554488331", "Gino Valerga", "987654321", "contacto@sportperu.com"),
        ("Representaciones Deportivas del Sur", "20448822119", "Mónica Sánchez", "985412630", "ventas@depsur.com.pe"),
        ("Importaciones Calzado Elite S.A.", "20601234567", "Raúl Castro", "993322110", "rcastro@calzadoelite.com"),
        ("Textiles y Confecciones Sport SAC", "20108877665", "Elena Rivas", "944556677", "erivas@textilsport.com"),
        ("Nike Corporate Perú (Representante)", "20309988776", "Juan Pérez", "911223344", "jperez@nikeperu.com"),
        ("Adidas Wholesale Group Sucursal", "20504030201", "Karen Müller", "922334455", "karen.muller@adidas.com"),
        ("Puma Sports Sucursal del Perú", "20405060708", "Diego Maradona", "933445566", "diego.maradona@puma.com"),
        ("Under Armour Distributor SAC", "20609080706", "Stephen Curry", "944556677", "scurry@uaperu.com"),
        ("Accesorios Deportivos Globals", "20112233445", "Luis Advíncula", "955667788", "ladvincula@sportglobals.com"),
        ("Logística y Calzado del Norte", "20778899001", "Paolo Guerrero", "966778899", "pguerrero@calzadonorte.com")
    ]
    
    sql_lines.append("PRINT 'Insertando Proveedores...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Proveedor] ON;")
    for i, prov in enumerate(proveedores_data, 1):
        sql_lines.append(f"INSERT INTO [dbo].[Proveedor] (id_proveedor, razon_social, ruc_o_documento, nombre_contacto, telefono, email) VALUES ({i}, '{prov[0]}', '{prov[1]}', '{prov[2]}', '{prov[3]}', '{prov[4]}');")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Proveedor] OFF;")
    sql_lines.append("GO\n")
    
    # 9. PEDIDOS DE CLIENTES (300 pedidos)
    estados_pedido = ["Pendiente", "Enviado", "Entregado"]
    
    pedidos = []
    detalles_pedido = []
    dp_counter = 1
    
    sql_lines.append("PRINT 'Insertando Pedidos y sus Detalles...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Pedido] ON;")
    
    for id_ped in range(1, 301):
        cliente = random.choice(clientes)
        id_cli = cliente[0]
        fecha_ped = cliente[6] + timedelta(days=random.randint(1, 60))
        if fecha_ped > datetime.now():
            fecha_ped = datetime.now() - timedelta(hours=random.randint(1, 24))
            
        fecha_ped_str = fecha_ped.strftime("%Y-%m-%d %H:%M:%S")
        estado = random.choice(estados_pedido)
        
        num_detalles = random.randint(1, 4)
        variantes_pedido = random.sample(variantes, num_detalles)
        
        total_pedido = 0
        detalles_temp = []
        
        for var in variantes_pedido:
            id_var = var[0]
            id_prod = var[1]
            prod_info = next(p for p in productos if p[0] == id_prod)
            precio_base = prod_info[6]
            precio_venta = round(precio_base * random.choice([0.9, 0.95, 1.0, 1.0, 1.05]), 2)
            cantidad = random.randint(1, 3)
            
            subtotal = precio_venta * cantidad
            total_pedido += subtotal
            
            detalles_temp.append((id_var, cantidad, precio_venta))
            
        total_pedido = round(total_pedido, 2)
        pedidos.append((id_ped, id_cli, fecha_ped, estado, total_pedido))
        
        sql_lines.append(f"INSERT INTO [dbo].[Pedido] (id_pedido, id_cliente, fecha_compra, estado_pedido, total) VALUES ({id_ped}, {id_cli}, '{fecha_ped_str}', '{estado}', {total_pedido});")
        
        for det in detalles_temp:
            detalles_pedido.append((dp_counter, id_ped, det[0], det[1], det[2]))
            dp_counter += 1
            
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Pedido] OFF;")
    sql_lines.append("GO\n")
    
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Detalle_Pedido] ON;")
    for id_dp, id_ped, id_var, cant, prec in detalles_pedido:
        sql_lines.append(f"INSERT INTO [dbo].[Detalle_Pedido] (id_detalle, id_pedido, id_variante, cantidad, precio_unitario) VALUES ({id_dp}, {id_ped}, {id_var}, {cant}, {prec});")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Detalle_Pedido] OFF;")
    sql_lines.append("GO\n")
    
    # 10. ORDENES DE COMPRA A PROVEEDORES (50 órdenes)
    estados_compra = ["Pendiente", "Enviado", "Entregado"]
    
    ordenes_compra = []
    detalles_compra = []
    dc_counter = 1
    
    sql_lines.append("PRINT 'Insertando Órdenes de Compra y sus Detalles...';")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Orden_Compra] ON;")
    
    for id_oc in range(1, 51):
        id_prov = random.randint(1, len(proveedores_data))
        fecha_emision = datetime.now() - timedelta(days=random.randint(10, 180))
        fecha_emision_str = fecha_emision.strftime("%Y-%m-%d %H:%M:%S")
        estado = random.choice(estados_compra)
        
        num_detalles = random.randint(2, 5)
        variantes_compra = random.sample(variantes, num_detalles)
        
        costo_total = 0
        detalles_temp = []
        
        for var in variantes_compra:
            id_var = var[0]
            id_prod = var[1]
            prod_info = next(p for p in productos if p[0] == id_prod)
            precio_base = prod_info[6]
            costo_unitario = round(precio_base * random.uniform(0.5, 0.7), 2)
            cantidad = random.randint(10, 50)
            
            subtotal = costo_unitario * cantidad
            costo_total += subtotal
            
            detalles_temp.append((id_var, cantidad, costo_unitario))
            
        costo_total = round(costo_total, 2)
        ordenes_compra.append((id_oc, id_prov, fecha_emision, estado, costo_total))
        
        sql_lines.append(f"INSERT INTO [dbo].[Orden_Compra] (id_orden_compra, id_proveedor, fecha_emision, estado, costo_total) VALUES ({id_oc}, {id_prov}, '{fecha_emision_str}', '{estado}', {costo_total});")
        
        for det in detalles_temp:
            detalles_compra.append((dc_counter, id_oc, det[0], det[1], det[2]))
            dc_counter += 1
            
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Orden_Compra] OFF;")
    sql_lines.append("GO\n")
    
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Detalle_Compra] ON;")
    for id_dc, id_oc, id_var, cant, costo in detalles_compra:
        sql_lines.append(f"INSERT INTO [dbo].[Detalle_Compra] (id_detalle_compra, id_orden_compra, id_variante, cantidad, costo_unitario) VALUES ({id_dc}, {id_oc}, {id_var}, {cant}, {costo});")
    sql_lines.append("SET IDENTITY_INSERT [dbo].[Detalle_Compra] OFF;")
    sql_lines.append("GO\n")
    
    sql_lines.append("PRINT '¡Todos los datos de prueba han sido insertados exitosamente!';")
    sql_lines.append("GO")
    
    # Escribir el archivo
    output_path = os.path.join(os.path.dirname(__file__), "inserts_datos_prueba.sql")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))
        
    print(f"Archivo {output_path} generado con éxito conteniendo {len(sql_lines)} líneas de código SQL.")

if __name__ == "__main__":
    main()
