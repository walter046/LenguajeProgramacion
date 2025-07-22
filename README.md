# **Proyecto Flask: Tienda Zapatillas**  

Este es un proyecto básico en **Python Flask** que incluye configuración para entornos virtuales y despliegue local.  


## **📂 Estructura del proyecto**

```text
tienda-zapatillas/
├── .github/                 # Configuración de GitHub (si aplica)
├── .venv/                   # Entorno virtual de Python
├── routes/                  # Módulos de rutas del backend
│   ├── admin.py             # Rutas del panel administrativo general
│   ├── auth.py              # Rutas de autenticación/login
│   ├── carritoadm.py        # Rutas del carrito para administrador
│   ├── cart.py              # Rutas del carrito para el cliente
│   ├── dashboardadm.py      # Rutas del dashboard del administrador
│   ├── main.py              # Rutas principales de la aplicación
│   ├── pedidos.py           # Rutas de pedidos del usuario
│   ├── pedidosadm.py        # Rutas de pedidos para el administrador
│   ├── products.py          # Rutas relacionadas a productos
│   ├── user.py              # Rutas de usuarios cliente
│   ├── usuariosadm.py       # Rutas para gestión de usuarios admin
│   └── zapatillasadm.py     # Rutas para gestionar zapatillas en admin
│
├── static/                  # Archivos estáticos (CSS, JS, imágenes)
│
├── templates/               # Plantillas HTML (vistas)
│   ├── admin/               # Plantillas del panel administrativo
│   ├── auth/                # Plantillas de autenticación
│   ├── app.html             
│   ├── carrito.html         # Plantillas del carrito
│   ├── carritoadm.html      # Plantillas de administrador carrito
│   ├── checkout.html        # Plantillas de verificacion de pago
│   ├── dashboard.html       # Plantillas de usuario
│   ├── dashboardadm.html    # Plantillas de administrador 
│   ├── detalle_products.html# Plantillas de detalles del pedido
│   ├── index.html           # Plantillas de index principal 
│   ├── mis_pedidos.html     # Plantillas de pediso
│   ├── pedidosadm.html      # Plantillas de administrador pedidos
│   ├── products.html        # Plantillas de productos
│   ├── usuariosadm.html     # Plantillas de administrador usuarios
│   └── zapatillasadm.html   # Plantillas de administrador zapatillas
│
├── app.py                   # Archivo principal que ejecuta la aplicación Flask
├── config.py                # Configuración de la app (base de datos, claves, etc.)
├── extensions.py            # Configuración de extensiones (DB, CSRF, login, etc.)
├── forms.py                 # Formulario con Flask-WTF
├── requirements.txt         # Lista de dependencias (Flask, Flask-Login, etc.)
└── README.md                # Documentación del proyecto

```

## **🚀 Configuración inicial**  

### **1. Clonar el repositorio**
```bash
https://github.com/walter046/LenguajeProgramacion.git
```

### **2. Instalar los requirements**
```bash
pip install -r requirements.txt
```

### **2. Activar el entorno virtual**
```bash
.\.venv\Scripts\activate
```

### **3. Ejecutar la aplicación**
```bash
python app.py
```
