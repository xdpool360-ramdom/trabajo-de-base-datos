-- ==========================================
-- SCRIPT DE REPORTES Y CONSULTAS ANALÍTICAS
-- BASE DE DATOS: Tienda_Total_Sport
-- ==========================================

USE [Tienda_Total_Sport];
GO

-- ============================================================================
-- SECCIÓN 1: REPORTES DE STOCK E INVENTARIO
-- ============================================================================

-- R001: Reporte de stock actual detallado por almacén y variante
PRINT 'Ejecutando R001...';
SELECT 
    a.nombre AS Almacen,
    p.nombre AS Producto,
    vp.talla AS Talla,
    vp.color AS Color,
    vp.sku AS SKU,
    i.cantidad_stock AS Stock,
    i.fecha_ultima_actualizacion AS UltimaActualizacion
FROM [dbo].[Inventario] i
INNER JOIN [dbo].[Almacen] a ON i.id_almacen = a.id_almacen
INNER JOIN [dbo].[Variante_Producto] vp ON i.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
ORDER BY a.nombre, p.nombre, vp.talla;
GO

-- R002: Alerta de stock crítico (Productos con stock inferior a 10 unidades en cualquier almacén)
PRINT 'Ejecutando R002...';
SELECT 
    a.nombre AS Almacen,
    p.nombre AS Producto,
    vp.sku AS SKU,
    i.cantidad_stock AS Stock
FROM [dbo].[Inventario] i
INNER JOIN [dbo].[Almacen] a ON i.id_almacen = a.id_almacen
INNER JOIN [dbo].[Variante_Producto] vp ON i.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
WHERE i.cantidad_stock < 10
ORDER BY i.cantidad_stock ASC;
GO

-- R003: Valorización del inventario por Almacén (Costo estimado según precio base)
PRINT 'Ejecutando R003...';
SELECT 
    a.nombre AS Almacen,
    COUNT(DISTINCT vp.id_producto) AS ProductosDistintos,
    SUM(i.cantidad_stock) AS TotalUnidades,
    SUM(i.cantidad_stock * p.precio_base) AS ValorizacionPrecioBase
FROM [dbo].[Inventario] i
INNER JOIN [dbo].[Almacen] a ON i.id_almacen = a.id_almacen
INNER JOIN [dbo].[Variante_Producto] vp ON i.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
GROUP BY a.nombre;
GO

-- R004: Stock total consolidated por producto (Suma de todos los almacenes)
PRINT 'Ejecutando R004...';
SELECT 
    p.nombre AS Producto,
    m.nombre AS Marca,
    c.nombre AS Categoria,
    SUM(i.cantidad_stock) AS StockTotalConsolidado
FROM [dbo].[Inventario] i
INNER JOIN [dbo].[Variante_Producto] vp ON i.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
INNER JOIN [dbo].[Marca] m ON p.id_marca = m.id_marca
INNER JOIN [dbo].[Categoria] c ON p.id_categoria = c.id_categoria
GROUP BY p.nombre, m.nombre, c.nombre
ORDER BY StockTotalConsolidado DESC;
GO

-- R005: Cantidad de variantes sin stock en ningún almacén (Stock cero)
PRINT 'Ejecutando R005...';
SELECT 
    p.nombre AS Producto,
    vp.sku AS SKU,
    vp.talla AS Talla,
    vp.color AS Color
FROM [dbo].[Variante_Producto] vp
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
WHERE vp.id_variante NOT IN (
    SELECT DISTINCT id_variante 
    FROM [dbo].[Inventario] 
    WHERE cantidad_stock > 0
);
GO

-- R006: Distribución del inventario por categoría
PRINT 'Ejecutando R006...';
SELECT 
    c.nombre AS Categoria,
    SUM(i.cantidad_stock) AS TotalStock,
    AVG(p.precio_base) AS PrecioPromedioCategoria,
    SUM(i.cantidad_stock * p.precio_base) AS ValorTotalInventario
FROM [dbo].[Inventario] i
INNER JOIN [dbo].[Variante_Producto] vp ON i.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
INNER JOIN [dbo].[Categoria] c ON p.id_categoria = c.id_categoria
GROUP BY c.nombre
ORDER BY TotalStock DESC;
GO

-- R007: Distribución del inventario por Marca
PRINT 'Ejecutando R007...';
SELECT 
    m.nombre AS Marca,
    SUM(i.cantidad_stock) AS TotalStock,
    SUM(i.cantidad_stock * p.precio_base) AS ValorTotalInventario
FROM [dbo].[Inventario] i
INNER JOIN [dbo].[Variante_Producto] vp ON i.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
INNER JOIN [dbo].[Marca] m ON p.id_marca = m.id_marca
GROUP BY m.nombre
ORDER BY TotalStock DESC;
GO

-- R008: Stock por género del producto (Hombre, Mujer, Unisex)
PRINT 'Ejecutando R008...';
SELECT 
    p.genero AS Genero,
    SUM(i.cantidad_stock) AS UnidadesEnInventario,
    COUNT(DISTINCT p.id_producto) AS TotalProductos
FROM [dbo].[Inventario] i
INNER JOIN [dbo].[Variante_Producto] vp ON i.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
GROUP BY p.genero;
GO


-- ============================================================================
-- SECCIÓN 2: REPORTES DE VENTAS (PEDIDOS) Y ESTADOS
-- ============================================================================

-- R009: Total de ventas cobradas acumuladas (Estado 'Entregado')
PRINT 'Ejecutando R009...';
SELECT 
    SUM(total) AS IngresosTotalesCobrados,
    COUNT(id_pedido) AS TransaccionesCompletadas
FROM [dbo].[Pedido]
WHERE estado_pedido = 'Entregado';
GO

-- R010: Ventas mensuales acumuladas de los últimos meses
PRINT 'Ejecutando R010...';
SELECT 
    YEAR(fecha_compra) AS Anio,
    MONTH(fecha_compra) AS Mes,
    COUNT(id_pedido) AS CantidadPedidos,
    SUM(total) AS VentasTotales
FROM [dbo].[Pedido]
GROUP BY YEAR(fecha_compra), MONTH(fecha_compra)
ORDER BY Anio DESC, Mes DESC;
GO

-- R011: Consolidado de pedidos por estado ('Pendiente', 'Enviado', 'Entregado')
PRINT 'Ejecutando R011...';
SELECT 
    estado_pedido AS Estado,
    COUNT(id_pedido) AS TotalPedidos,
    SUM(total) AS MontoTotalAsociado
FROM [dbo].[Pedido]
GROUP BY estado_pedido;
GO

-- R012: Ticket promedio de venta de pedidos entregados
PRINT 'Ejecutando R012...';
SELECT 
    AVG(total) AS TicketPromedioVenta,
    MAX(total) AS PedidoMasCaro,
    MIN(total) AS PedidoMasBarato
FROM [dbo].[Pedido]
WHERE estado_pedido = 'Entregado';
GO

-- R013: Productos más vendidos (Top 15 por cantidad vendida)
PRINT 'Ejecutando R013...';
SELECT TOP 15
    p.nombre AS Producto,
    m.nombre AS Marca,
    c.nombre AS Categoria,
    SUM(dp.cantidad) AS UnidadesVendidas,
    SUM(dp.cantidad * dp.precio_unitario) AS FacturacionTotal
FROM [dbo].[Detalle_Pedido] dp
INNER JOIN [dbo].[Variante_Producto] vp ON dp.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
INNER JOIN [dbo].[Marca] m ON p.id_marca = m.id_marca
INNER JOIN [dbo].[Categoria] c ON p.id_categoria = c.id_categoria
INNER JOIN [dbo].[Pedido] ped ON dp.id_pedido = ped.id_pedido
WHERE ped.estado_pedido = 'Entregado'
GROUP BY p.nombre, m.nombre, c.nombre
ORDER BY UnidadesVendidas DESC;
GO

-- R014: Ventas totales por Marca deportiva
PRINT 'Ejecutando R014...';
SELECT 
    m.nombre AS Marca,
    SUM(dp.cantidad) AS UnidadesVendidas,
    SUM(dp.cantidad * dp.precio_unitario) AS TotalVentas
FROM [dbo].[Detalle_Pedido] dp
INNER JOIN [dbo].[Variante_Producto] vp ON dp.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
INNER JOIN [dbo].[Marca] m ON p.id_marca = m.id_marca
INNER JOIN [dbo].[Pedido] ped ON dp.id_pedido = ped.id_pedido
WHERE ped.estado_pedido = 'Entregado'
GROUP BY m.nombre
ORDER BY TotalVentas DESC;
GO

-- R015: Ventas totales por Categoría de producto
PRINT 'Ejecutando R015...';
SELECT 
    c.nombre AS Categoria,
    SUM(dp.cantidad) AS UnidadesVendidas,
    SUM(dp.cantidad * dp.precio_unitario) AS TotalVentas
FROM [dbo].[Detalle_Pedido] dp
INNER JOIN [dbo].[Variante_Producto] vp ON dp.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
INNER JOIN [dbo].[Categoria] c ON p.id_categoria = c.id_categoria
INNER JOIN [dbo].[Pedido] ped ON dp.id_pedido = ped.id_pedido
WHERE ped.estado_pedido = 'Entregado'
GROUP BY c.nombre
ORDER BY TotalVentas DESC;
GO

-- R016: Ventas por género de cliente (estimación o género del producto comprado)
PRINT 'Ejecutando R016...';
SELECT 
    p.genero AS GeneroProducto,
    SUM(dp.cantidad) AS UnidadesVendidas,
    SUM(dp.cantidad * dp.precio_unitario) AS TotalVentas
FROM [dbo].[Detalle_Pedido] dp
INNER JOIN [dbo].[Variante_Producto] vp ON dp.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
INNER JOIN [dbo].[Pedido] ped ON dp.id_pedido = ped.id_pedido
GROUP BY p.genero;
GO

-- R017: Pedidos Pendientes con datos de contacto del cliente (Para urgencias de despacho)
PRINT 'Ejecutando R017...';
SELECT 
    p.id_pedido AS NroPedido,
    p.fecha_compra AS FechaCompra,
    CONCAT(c.nombre, ' ', c.apellido) AS Cliente,
    c.telefono AS Telefono,
    c.email AS Email,
    p.total AS TotalPagar
FROM [dbo].[Pedido] p
INNER JOIN [dbo].[Cliente] c ON p.id_cliente = c.id_cliente
WHERE p.estado_pedido = 'Pendiente'
ORDER BY p.fecha_compra ASC;
GO

-- R018: Pedidos Enviados pero aún no entregados (En camino)
PRINT 'Ejecutando R018...';
SELECT 
    p.id_pedido AS NroPedido,
    p.fecha_compra AS FechaCompra,
    CONCAT(c.nombre, ' ', c.apellido) AS Cliente,
    c.direccion AS DireccionEntrega,
    p.total AS Total
FROM [dbo].[Pedido] p
INNER JOIN [dbo].[Cliente] c ON p.id_cliente = c.id_cliente
WHERE p.estado_pedido = 'Enviado'
ORDER BY p.fecha_compra ASC;
GO


-- ============================================================================
-- SECCIÓN 3: REPORTES DE CLIENTES
-- ============================================================================

-- R019: Top 15 Clientes VIP (Mayores compras totales realizadas)
PRINT 'Ejecutando R019...';
SELECT TOP 15
    c.id_cliente AS ID,
    CONCAT(c.nombre, ' ', c.apellido) AS Cliente,
    c.email AS Email,
    COUNT(p.id_pedido) AS TotalPedidosRealizados,
    SUM(p.total) AS MontoTotalGastado
FROM [dbo].[Cliente] c
INNER JOIN [dbo].[Pedido] p ON c.id_cliente = p.id_cliente
WHERE p.estado_pedido = 'Entregado'
GROUP BY c.id_cliente, c.nombre, c.apellido, c.email
ORDER BY MontoTotalGastado DESC;
GO

-- R020: Clientes inactivos (Que no han realizado ningún pedido en la tienda)
PRINT 'Ejecutando R020...';
SELECT 
    c.id_cliente AS ID,
    CONCAT(c.nombre, ' ', c.apellido) AS Cliente,
    c.email AS Email,
    c.telefono AS Telefono,
    c.fecha_registro AS FechaRegistro
FROM [dbo].[Cliente] c
LEFT JOIN [dbo].[Pedido] p ON c.id_cliente = p.id_cliente
WHERE p.id_pedido IS NULL
ORDER BY c.fecha_registro DESC;
GO

-- R021: Distribución geográfica de clientes por distrito de Lima
PRINT 'Ejecutando R021...';
-- Asumiendo formato de dirección de ejemplo: '..., [Distrito], Lima'
SELECT 
    SUBSTRING(
        direccion, 
        CHARINDEX(',', direccion) + 2, 
        CHARINDEX(',', direccion, CHARINDEX(',', direccion) + 1) - CHARINDEX(',', direccion) - 2
    ) AS Distrito,
    COUNT(id_cliente) AS TotalClientes
FROM [dbo].[Cliente]
GROUP BY 
    SUBSTRING(
        direccion, 
        CHARINDEX(',', direccion) + 2, 
        CHARINDEX(',', direccion, CHARINDEX(',', direccion) + 1) - CHARINDEX(',', direccion) - 2
    )
ORDER BY TotalClientes DESC;
GO

-- R022: Tasa de recompra de clientes (Clientes que han comprado más de una vez)
PRINT 'Ejecutando R022...';
SELECT 
    COUNT(CASE WHEN Pedidos > 1 THEN 1 END) AS ClientesRecurrentes,
    COUNT(*) AS ClientesConAlMenosUnPedido,
    (CAST(COUNT(CASE WHEN Pedidos > 1 THEN 1 END) AS FLOAT) / COUNT(*)) * 100 AS PorcentajeRecompra
FROM (
    SELECT id_cliente, COUNT(id_pedido) AS Pedidos
    FROM [dbo].[Pedido]
    GROUP BY id_cliente
) AS ResumenPedidosCliente;
GO


-- ============================================================================
-- SECCIÓN 4: REPORTES DE COMPRAS Y PROVEEDORES
-- ============================================================================

-- R023: Costo total invertido en compras por proveedor (Historial consolidado)
PRINT 'Ejecutando R023...';
SELECT 
    prov.razon_social AS Proveedor,
    prov.ruc_o_documento AS RUC,
    COUNT(oc.id_orden_compra) AS TotalOrdenes,
    SUM(oc.costo_total) AS TotalGastado
FROM [dbo].[Orden_Compra] oc
INNER JOIN [dbo].[Proveedor] prov ON oc.id_proveedor = prov.id_proveedor
WHERE oc.estado = 'Entregado'
GROUP BY prov.razon_social, prov.ruc_o_documento
ORDER BY TotalGastado DESC;
GO

-- R024: Órdenes de compra pendientes de recibir
PRINT 'Ejecutando R024...';
SELECT 
    oc.id_orden_compra AS NroOrden,
    prov.razon_social AS Proveedor,
    oc.fecha_emision AS FechaEmision,
    oc.estado AS Estado,
    oc.costo_total AS CostoTotal
FROM [dbo].[Orden_Compra] oc
INNER JOIN [dbo].[Proveedor] prov ON oc.id_proveedor = prov.id_proveedor
WHERE oc.estado IN ('Pendiente', 'Enviado')
ORDER BY oc.fecha_emision ASC;
GO

-- R025: Volumen de unidades compradas a proveedores por variante de producto
PRINT 'Ejecutando R025...';
SELECT 
    p.nombre AS Producto,
    vp.sku AS SKU,
    vp.talla AS Talla,
    vp.color AS Color,
    SUM(dc.cantidad) AS CantidadUnidadesCompradas,
    SUM(dc.cantidad * dc.costo_unitario) AS CostoTotalAdquisicion
FROM [dbo].[Detalle_Compra] dc
INNER JOIN [dbo].[Variante_Producto] vp ON dc.id_variante = vp.id_variante
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
GROUP BY p.nombre, vp.sku, vp.talla, vp.color
ORDER BY CantidadUnidadesCompradas DESC;
GO


-- ============================================================================
-- SECCIÓN 5: ANÁLISIS DE EFICIENCIA, RENDIMIENTO Y RENTABILIDAD
-- ============================================================================

-- R026: Margen de ganancia bruto por producto (Precio de venta promedio vs Costo de compra promedio)
PRINT 'Ejecutando R026...';
WITH CostosPromedio AS (
    SELECT id_variante, AVG(costo_unitario) AS CostoPromedio
    FROM [dbo].[Detalle_Compra]
    GROUP BY id_variante
),
VentasPromedio AS (
    SELECT id_variante, AVG(precio_unitario) AS PrecioPromedio
    FROM [dbo].[Detalle_Pedido]
    GROUP BY id_variante
)
SELECT TOP 20
    p.nombre AS Producto,
    vp.sku AS SKU,
    cp.CostoPromedio AS CostoPromedioCompra,
    vp2.PrecioPromedio AS PrecioPromedioVenta,
    (vp2.PrecioPromedio - cp.CostoPromedio) AS UtilidadPorUnidad,
    ((vp2.PrecioPromedio - cp.CostoPromedio) / vp2.PrecioPromedio) * 100 AS MargenPorcentaje
FROM [dbo].[Variante_Producto] vp
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
INNER JOIN CostosPromedio cp ON vp.id_variante = cp.id_variante
INNER JOIN VentasPromedio vp2 ON vp.id_variante = vp2.id_variante
ORDER BY MargenPorcentaje DESC;
GO

-- R027: Comparación histórica mensual: Ventas vs Compras (Flujo de caja de mercadería)
PRINT 'Ejecutando R027...';
WITH VentasMensuales AS (
    SELECT 
        YEAR(fecha_compra) AS Anio,
        MONTH(fecha_compra) AS Mes,
        SUM(total) AS TotalVentas
    FROM [dbo].[Pedido]
    WHERE estado_pedido = 'Entregado'
    GROUP BY YEAR(fecha_compra), MONTH(fecha_compra)
),
ComprasMensuales AS (
    SELECT 
        YEAR(fecha_emision) AS Anio,
        MONTH(fecha_emision) AS Mes,
        SUM(costo_total) AS TotalCompras
    FROM [dbo].[Orden_Compra]
    WHERE estado = 'Entregado'
    GROUP BY YEAR(fecha_emision), MONTH(fecha_emision)
)
SELECT 
    COALESCE(v.Anio, c.Anio) AS Anio,
    COALESCE(v.Mes, c.Mes) AS Mes,
    ISNULL(v.TotalVentas, 0) AS IngresosVentas,
    ISNULL(c.TotalCompras, 0) AS GastosCompras,
    (ISNULL(v.TotalVentas, 0) - ISNULL(c.TotalCompras, 0)) AS BalanceNetoMercaderia
FROM VentasMensuales v
FULL OUTER JOIN ComprasMensuales c ON v.Anio = c.Anio AND v.Mes = c.Mes
ORDER BY Anio DESC, Mes DESC;
GO

-- R028: Rotación de inventario (Unidades vendidas vs stock actual)
PRINT 'Ejecutando R028...';
SELECT 
    p.nombre AS Producto,
    vp.sku AS SKU,
    ISNULL(SUM(dp.cantidad), 0) AS UnidadesVendidas,
    ISNULL(MIN(i.cantidad_stock), 0) AS StockActual,
    CASE 
        WHEN ISNULL(MIN(i.cantidad_stock), 0) = 0 THEN 999.9 -- Evita división por cero, representa rotación rápida
        ELSE CAST(ISNULL(SUM(dp.cantidad), 0) AS FLOAT) / MIN(i.cantidad_stock)
    END AS IndiceRotacion
FROM [dbo].[Variante_Producto] vp
INNER JOIN [dbo].[Producto] p ON vp.id_producto = p.id_producto
LEFT JOIN [dbo].[Detalle_Pedido] dp ON vp.id_variante = dp.id_variante
LEFT JOIN [dbo].[Inventario] i ON vp.id_variante = i.id_variante
GROUP BY p.nombre, vp.sku
ORDER BY UnidadesVendidas DESC;
GO

-- R029: Rendimiento del stock por Categoría (Venta total / stock actual)
PRINT 'Ejecutando R029...';
SELECT 
    c.nombre AS Categoria,
    SUM(dp.cantidad) AS UnidadesVendidas,
    (SELECT SUM(cantidad_stock) 
     FROM [dbo].[Inventario] inv 
     INNER JOIN [dbo].[Variante_Producto] vp2 ON inv.id_variante = vp2.id_variante
     INNER JOIN [dbo].[Producto] prod2 ON vp2.id_producto = prod2.id_producto
     WHERE prod2.id_categoria = c.id_categoria) AS StockActual,
    SUM(dp.cantidad * dp.precio_unitario) AS TotalVendidoSoles
FROM [dbo].[Categoria] c
INNER JOIN [dbo].[Producto] p ON c.id_categoria = p.id_categoria
INNER JOIN [dbo].[Variante_Producto] vp ON p.id_producto = vp.id_producto
INNER JOIN [dbo].[Detalle_Pedido] dp ON vp.id_variante = dp.id_variante
GROUP BY c.id_categoria, c.nombre
ORDER BY TotalVendidoSoles DESC;
GO

-- R030: Clientes con mayor número de pedidos cancelados/pendientes prolongados
PRINT 'Ejecutando R030...';
SELECT 
    c.id_cliente AS IDCliente,
    CONCAT(c.nombre, ' ', c.apellido) AS NombreCliente,
    COUNT(CASE WHEN p.estado_pedido = 'Pendiente' THEN 1 END) AS PedidosPendientes,
    COUNT(p.id_pedido) AS PedidosTotales,
    (CAST(COUNT(CASE WHEN p.estado_pedido = 'Pendiente' THEN 1 END) AS FLOAT) / COUNT(p.id_pedido)) * 100 AS PorcentajePendientes
FROM [dbo].[Cliente] c
INNER JOIN [dbo].[Pedido] p ON c.id_cliente = p.id_cliente
GROUP BY c.id_cliente, c.nombre, c.apellido
HAVING COUNT(p.id_pedido) >= 2
ORDER BY PedidosPendientes DESC;
GO

PRINT '¡Script de reportes y consultas analíticas completado con éxito!';
GO
