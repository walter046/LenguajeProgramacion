# Integración de Imágenes en la Base de Datos

Este documento explica cómo se ha implementado la funcionalidad para mostrar imágenes de zapatillas en la aplicación.

## Cambios Realizados

### 1. Base de Datos

Se agregó una nueva columna `imagen` a la tabla `zapatillas` para almacenar el nombre del archivo de imagen correspondiente.

**Estructura actualizada:**
```sql
CREATE TABLE `zapatillas` (
  `id_zapatilla` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,  -- Nueva columna
  `id_marca` int DEFAULT NULL,
  PRIMARY KEY (`id_zapatilla`),
  KEY `id_marca` (`id_marca`),
  CONSTRAINT `zapatillas_ibfk_1` FOREIGN KEY (`id_marca`) REFERENCES `marcas` (`id_marca`)
);
```

### 2. Imágenes Asociadas

Las siguientes zapatillas tienen imágenes asociadas:

| ID | Zapatilla | Marca | Imagen |
|----|-----------|-------|--------|
| 1 | Air Max 90 | Nike | nike.png |
| 2 | Ultraboost 22 | Adidas | adidas.png |
| 3 | RS-X Reinvention | Puma | puma.png |
| 4 | Classic Leather | Reebok | reebok.png |
| 5 | 574 Core | New Balance | Balance.png |

### 3. Aplicación Flask

Se actualizó la consulta SQL en la función `novedades()` para incluir la columna `imagen`:

```python
query = """
    SELECT
        z.id_zapatilla,
        z.nombre AS nombre_zapatilla,
        z.descripcion,
        z.precio AS precio,
        z.imagen,  -- Nueva columna
        m.nombre AS nombre_marca
    FROM
        zapatillas z
    JOIN
        marcas m ON z.id_marca = m.id_marca;
"""
```

### 4. Template HTML

Se rediseñó completamente el template `novedades.html` para mostrar las imágenes en un grid responsivo con cards modernas.

**Características del nuevo diseño:**
- Grid responsivo (1-4 columnas según el tamaño de pantalla)
- Cards con sombras y efectos hover
- Imágenes con fallback si no existen
- Diseño moderno con Tailwind CSS

## Instrucciones de Instalación

### Paso 1: Ejecutar el Script de Actualización

```bash
cd LenguajeProgramacion
python ejecutar_actualizacion.py
```

Este script:
- Verifica si la columna `imagen` existe
- La agrega si no existe
- Actualiza las zapatillas existentes con sus imágenes correspondientes
- Muestra una verificación de los cambios

### Paso 2: Verificar las Imágenes

Asegúrate de que las siguientes imágenes estén en la carpeta `static/img/`:
- `nike.png`
- `adidas.png`
- `puma.png`
- `reebok.png`
- `Balance.png`
- `usuario.png` (imagen de fallback)

### Paso 3: Ejecutar la Aplicación

```bash
python app.py
```

## Funcionalidades Implementadas

### 1. Paradigmas de Programación Integrados

**Programación Orientada a Objetos:**
- Clases para formularios (RegisterForm, LoginForm)
- Encapsulación de datos y métodos

**Programación Funcional:**
- Funciones puras para validaciones
- Uso de list comprehensions y funciones lambda
- Manejo de errores con try-catch

**Programación Estructurada:**
- Control de flujo con if/else
- Bucles for para iteraciones
- Modularización del código

### 2. Librerías Utilizadas

- **Flask**: Framework web
- **Flask-WTF**: Manejo de formularios
- **Flask-MySQLdb**: Conexión a base de datos
- **bcrypt**: Encriptación de contraseñas
- **Flask-Limiter**: Limitación de rate
- **mysql-connector**: Conexión directa a MySQL

### 3. Características de la Implementación

**Manejo de Imágenes:**
- Almacenamiento de nombres de archivo en la base de datos
- Servido estático de imágenes desde Flask
- Fallback para imágenes faltantes
- Optimización de carga con lazy loading

**Base de Datos:**
- Relaciones entre tablas (zapatillas ↔ marcas)
- Consultas JOIN para obtener datos relacionados
- Actualización segura de datos

**Interfaz de Usuario:**
- Diseño responsivo con Tailwind CSS
- Grid system para layout
- Efectos hover y transiciones
- Notificaciones en tiempo real

## Estructura de Archivos

```
LenguajeProgramacion/
├── app.py                          # Aplicación principal
├── bd.sql                          # Esquema de base de datos
├── update_images.sql               # Script SQL para actualizaciones
├── ejecutar_actualizacion.py       # Script Python para actualizar BD
├── static/
│   └── img/
│       ├── nike.png
│       ├── adidas.png
│       ├── puma.png
│       ├── reebok.png
│       ├── Balance.png
│       └── usuario.png
└── templates/
    └── novedades.html              # Template actualizado
```

## Solución de Problemas

### Error: "Columna imagen no existe"
Ejecuta el script `ejecutar_actualizacion.py` para agregar la columna.

### Error: "Imagen no encontrada"
Verifica que las imágenes estén en `static/img/` y que los nombres coincidan con los de la base de datos.

### Error: "No se puede conectar a MySQL"
Verifica que MySQL esté ejecutándose y que las credenciales en `app.py` sean correctas.

## Próximos Pasos

1. **Subir imágenes**: Implementar funcionalidad para que los administradores puedan subir nuevas imágenes
2. **Optimización**: Comprimir imágenes para mejorar el rendimiento
3. **CDN**: Implementar un CDN para servir imágenes más rápido
4. **Cache**: Implementar cache para las consultas de base de datos 