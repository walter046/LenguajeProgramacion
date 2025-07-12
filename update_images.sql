-- Script para agregar columna imagen y actualizar las zapatillas existentes
USE tienda_zapatillas;

-- Agregar columna imagen si no existe
ALTER TABLE zapatillas ADD COLUMN imagen VARCHAR(255) DEFAULT NULL AFTER precio;

-- Actualizar las zapatillas existentes con sus imágenes correspondientes
UPDATE zapatillas SET imagen = 'nike.png' WHERE id_zapatilla = 1; -- Air Max 90
UPDATE zapatillas SET imagen = 'adidas.png' WHERE id_zapatilla = 2; -- Ultraboost 22
UPDATE zapatillas SET imagen = 'puma.png' WHERE id_zapatilla = 3; -- RS-X Reinvention
UPDATE zapatillas SET imagen = 'reebok.png' WHERE id_zapatilla = 4; -- Classic Leather
UPDATE zapatillas SET imagen = 'Balance.png' WHERE id_zapatilla = 5; -- 574 Core

-- Verificar los cambios
SELECT id_zapatilla, nombre, imagen FROM zapatillas; 