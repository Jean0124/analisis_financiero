-- Tabla de categorías
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('ingreso', 'gasto'))
);

-- Tabla principal de transacciones
CREATE TABLE transacciones (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    descripcion VARCHAR(255),
    monto DECIMAL(12,2) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('ingreso', 'gasto')),
    categoria_id INT REFERENCES categorias(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vista de resumen mensual
CREATE VIEW resumen_mensual AS
SELECT
    DATE_TRUNC('month', fecha) AS mes,
    tipo,
    SUM(monto) AS total,
    COUNT(*) AS num_transacciones
FROM transacciones
GROUP BY DATE_TRUNC('month', fecha), tipo
ORDER BY mes DESC;

-- Vista de gastos por categoría
CREATE VIEW gastos_por_categoria AS
SELECT
    c.nombre AS categoria,
    SUM(t.monto) AS total,
    COUNT(*) AS num_transacciones,
    ROUND(SUM(t.monto) * 100.0 / SUM(SUM(t.monto)) OVER (), 2) AS porcentaje
FROM transacciones t
JOIN categorias c ON t.categoria_id = c.id
WHERE t.tipo = 'gasto'
GROUP BY c.nombre
ORDER BY total DESC;