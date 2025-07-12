# Integración de URLs de Imágenes Externas

Este documento explica cómo se ha implementado la funcionalidad para mostrar imágenes de zapatillas desde URLs externas.

## Cambios Realizados

### 1. Base de Datos

La columna `imagen` en la tabla `zapatillas` ahora almacena URLs completas en lugar de nombres de archivo locales.

**Ejemplo de datos:**
```sql
UPDATE zapatillas 
SET imagen = 'https://antonioperu.com/cdn/shop/files/WQEWQEWEQEE_2.jpg?v=1724977705&width=1920'
WHERE id_zapatilla = 5;
```

### 2. Template HTML Actualizado

Se modificó el template `novedades.html` para:

- **Usar URLs directas**: `<img src="{{ zapatilla.imagen }}">`
- **Lazy loading**: `loading="lazy"` para mejor rendimiento
- **Efectos hover**: `hover:scale-105` para zoom al pasar el mouse
- **Spinner de carga**: Indicador visual mientras se cargan las imágenes
- **Fallback**: Imagen por defecto si la URL falla

### 3. Características Implementadas

#### **Optimización de Rendimiento:**
- Lazy loading para cargar imágenes solo cuando son visibles
- Spinner de carga para mejor UX
- Transiciones suaves con CSS

#### **Manejo de Errores:**
- Fallback automático si la imagen no carga
- Ocultar spinner en caso de error
- Imagen por defecto (`usuario.png`) como respaldo

#### **Efectos Visuales:**
- Hover con zoom suave
- Sombras dinámicas
- Transiciones fluidas

## URLs de Ejemplo

El script `actualizar_urls_imagenes.py` incluye URLs de ejemplo:

| Zapatilla | URL de Imagen |
|-----------|---------------|
| Air Max 90 | `https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop` |
| Ultraboost 22 | `https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop` |
| RS-X Reinvention | `https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop` |
| Classic Leather | `https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=400&h=400&fit=crop` |
| 574 Core | `https://antonioperu.com/cdn/shop/files/WQEWQEWEQEE_2.jpg?v=1724977705&width=1920` |

## Instrucciones de Uso

### Paso 1: Actualizar URLs de Imágenes

```bash
cd LenguajeProgramacion
python actualizar_urls_imagenes.py
```

### Paso 2: Personalizar URLs

Edita el archivo `actualizar_urls_imagenes.py` y cambia las URLs por las que prefieras:

```python
actualizaciones = [
    (1, 'TU_URL_AQUI', 'Air Max 90 - Nike'),
    (2, 'TU_URL_AQUI', 'Ultraboost 22 - Adidas'),
    # ... más URLs
]
```

### Paso 3: Ejecutar la Aplicación

```bash
python app.py
```

## Ventajas de Usar URLs Externas

### **1. Flexibilidad:**
- Puedes usar imágenes de cualquier servidor
- No necesitas almacenar archivos localmente
- Fácil actualización de imágenes

### **2. Rendimiento:**
- CDNs pueden servir imágenes más rápido
- Reducción del tamaño de tu aplicación
- Mejor escalabilidad

### **3. Mantenimiento:**
- No necesitas gestionar archivos locales
- Actualizaciones centralizadas
- Menor complejidad de despliegue

## Paradigmas de Programación Implementados

### **Programación Orientada a Objetos:**
- Clases para manejo de formularios
- Encapsulación de datos de imágenes
- Métodos para validación de URLs

### **Programación Funcional:**
- Funciones puras para manejo de imágenes
- Event listeners para carga asíncrona
- Callbacks para manejo de errores

### **Programación Reactiva:**
- Eventos de carga de imágenes
- Actualizaciones dinámicas del DOM
- Manejo asíncrono de recursos

## Librerías y Tecnologías

- **Flask**: Servidor web
- **MySQL**: Base de datos
- **Tailwind CSS**: Estilos y animaciones
- **JavaScript ES6+**: Interactividad del lado cliente
- **HTML5**: Semántica y accesibilidad

## Estructura del Código

```html
<!-- Template con URLs externas -->
<img 
  src="{{ zapatilla.imagen }}" 
  alt="{{ zapatilla.nombre_zapatilla }}"
  class="w-full h-full object-contain p-4 transition-transform duration-300 hover:scale-105"
  onerror="this.src='{{ url_for('static', filename='img/usuario.png') }}'"
  loading="lazy"
  onload="this.style.opacity='1'"
  style="opacity: 0;"
>
```

```javascript
// JavaScript para manejo de imágenes
function handleImageLoad() {
  const images = document.querySelectorAll('img[loading="lazy"]');
  images.forEach(img => {
    img.addEventListener('load', function() {
      // Ocultar spinner cuando la imagen se carga
      const spinnerId = 'spinner-' + this.closest('.zapatilla').querySelector('[data-id]').getAttribute('data-id');
      const spinner = document.getElementById(spinnerId);
      if (spinner) {
        spinner.style.display = 'none';
      }
    });
  });
}
```

## Solución de Problemas

### **Error: "Imagen no carga"**
- Verifica que la URL sea accesible
- Revisa la consola del navegador para errores CORS
- Asegúrate de que la URL sea válida

### **Error: "Spinner no se oculta"**
- Verifica que el ID del spinner coincida con el ID de la zapatilla
- Revisa la consola para errores de JavaScript

### **Error: "Imagen muy grande/pequeña"**
- Ajusta los parámetros de la URL (width, height)
- Usa servicios como Unsplash que permiten redimensionamiento

## Próximos Pasos

1. **Optimización**: Implementar compresión de imágenes en el servidor
2. **Cache**: Agregar cache para URLs de imágenes
3. **Validación**: Implementar validación de URLs antes de guardar
4. **CDN**: Configurar un CDN propio para mejor control
5. **Compresión**: Implementar formatos modernos como WebP 