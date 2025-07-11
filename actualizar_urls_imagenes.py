#!/usr/bin/env python3
"""
Script para actualizar las zapatillas con URLs de imágenes externas
"""

import mysql.connector
from mysql.connector import Error

def actualizar_urls_imagenes():
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
            
            # URLs de imágenes externas para cada zapatilla
            # Puedes reemplazar estas URLs con las que prefieras
            actualizaciones = [
                (1, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop', 'Air Max 90 - Nike'),
                (2, 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop', 'Ultraboost 22 - Adidas'),
                (3, 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop', 'RS-X Reinvention - Puma'),
                (4, 'https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=400&h=400&fit=crop', 'Classic Leather - Reebok'),
                (5, 'https://antonioperu.com/cdn/shop/files/WQEWQEWEQEE_2.jpg?v=1724977705&width=1920', '574 Core - New Balance')
            ]
            
            print("Actualizando URLs de imágenes...")
            
            for id_zapatilla, url_imagen, nombre in actualizaciones:
                cursor.execute("UPDATE zapatillas SET imagen = %s WHERE id_zapatilla = %s", (url_imagen, id_zapatilla))
                print(f"✓ Actualizada zapatilla {nombre} (ID: {id_zapatilla}) con URL: {url_imagen}")
            
            connection.commit()
            
            cursor.execute("SELECT id_zapatilla, nombre, imagen FROM zapatillas")
            resultados = cursor.fetchall()
            
            print("\n=== Verificación de cambios ===")
            for resultado in resultados:
                print(f"ID: {resultado[0]}, Nombre: {resultado[1]}")
                print(f"URL: {resultado[2]}")
                print("-" * 50)
            
            print("\n✓ URLs actualizadas exitosamente!")
            
    except Error as e:
        print(f"Error al conectar con MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada")

if __name__ == "__main__":
    print("Iniciando actualización de URLs de imágenes...")
    actualizar_urls_imagenes() 