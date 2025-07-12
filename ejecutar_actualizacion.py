#!/usr/bin/env python3
"""
Script para actualizar la base de datos con las imágenes de zapatillas
"""

import mysql.connector
from mysql.connector import Error

def actualizar_base_datos():
    try:
        # Configuración de la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='karjoel',
            database='tienda_zapatillas'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar si la columna imagen ya existe
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'tienda_zapatillas' 
                AND TABLE_NAME = 'zapatillas' 
                AND COLUMN_NAME = 'imagen'
            """)
            
            columna_existe = cursor.fetchone()
            
            if not columna_existe:
                print("Agregando columna 'imagen' a la tabla zapatillas...")
                cursor.execute("ALTER TABLE zapatillas ADD COLUMN imagen VARCHAR(255) DEFAULT NULL AFTER precio")
                connection.commit()
                print("✓ Columna 'imagen' agregada exitosamente")
            else:
                print("✓ La columna 'imagen' ya existe")
            
            # Actualizar las zapatillas con sus imágenes correspondientes
            actualizaciones = [
                (1, 'nike.png', 'Air Max 90'),
                (2, 'adidas.png', 'Ultraboost 22'),
                (3, 'puma.png', 'RS-X Reinvention'),
                (4, 'reebok.png', 'Classic Leather'),
                (5, 'Balance.png', '574 Core')
            ]
            
            for id_zapatilla, imagen, nombre in actualizaciones:
                cursor.execute("UPDATE zapatillas SET imagen = %s WHERE id_zapatilla = %s", (imagen, id_zapatilla))
                print(f"✓ Actualizada zapatilla {nombre} (ID: {id_zapatilla}) con imagen: {imagen}")
            
            connection.commit()
            
            # Verificar los cambios
            cursor.execute("SELECT id_zapatilla, nombre, imagen FROM zapatillas")
            resultados = cursor.fetchall()
            
            print("\n=== Verificación de cambios ===")
            for resultado in resultados:
                print(f"ID: {resultado[0]}, Nombre: {resultado[1]}, Imagen: {resultado[2]}")
            
            print("\n✓ Actualización completada exitosamente!")
            
    except Error as e:
        print(f"Error al conectar con MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada")

if __name__ == "__main__":
    print("Iniciando actualización de la base de datos...")
    actualizar_base_datos() 