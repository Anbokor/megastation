# Agentes y Roles del Sistema

Este documento describe los diferentes tipos de usuarios (agentes) que interactúan con el sistema, sus roles y sus responsabilidades principales.

---

## 1. Cliente (`customer`)

Es el usuario final de la plataforma. Este es el rol por defecto para cualquier persona que se registra en el sitio.

**Responsabilidades y Capacidades:**
- Navegar por el catálogo de productos.
- Agregar productos a su carrito de compras.
- Realizar pedidos (`Checkout`).
- Ver su propio historial de pedidos.
- No tiene acceso a ningún panel de administración o gestión.

---

## 2. Vendedor (`seller`)

Es un empleado asociado a un **Punto de Venta** (`SalesPoint`) específico. Su función principal es la gestión de pedidos en su tienda.

**Responsabilidades y Capacidades:**
- Ver la lista de pedidos asignados a su punto de venta.
- Acceder a los detalles de un pedido específico.
- **Gestionar el estado de los pedidos** (ej: cambiar de `pendiente` a `en_proceso` o `enviado`).
- Recibe notificaciones por correo electrónico sobre nuevos pedidos en su tienda.

---

## 3. Administrador de Tienda (`store_admin`)

Es un rol de gestión superior, también asociado a un **Punto de Venta** (`SalesPoint`) específico. Tiene todas las capacidades de un Vendedor, más responsabilidades adicionales sobre el inventario y la analítica de su tienda.

**Responsabilidades y Capacidades:**
- Todas las capacidades de un **Vendedor**.
- Acceder al **Dashboard de Analíticas** para ver las métricas de rendimiento (KPIs, gráficos) **de su propia tienda**.
- Gestionar el inventario (`Stock`) de los productos en su punto de venta.
- Crear y gestionar facturas de compra (`Invoices`) para su tienda.

---

## 4. Administrador General (`admin`)

Es un rol de alta jerarquía que no está limitado a un punto de venta. Supervisa toda la operación de la plataforma.

**Responsabilidades y Capacidades:**
- Acceder al **Dashboard de Analíticas** con una vista global de **todas las tiendas**.
- Gestionar usuarios: crear, editar y eliminar otros usuarios (excepto Superusuarios y otros Administradores).
- Tiene acceso completo a la gestión de productos, categorías, pedidos e inventario de toda la plataforma.

---

## 5. Superusuario (`superuser`)

Es el rol con el máximo nivel de acceso. Generalmente reservado para los desarrolladores o administradores principales del sistema.

**Responsabilidades y Capacidades:**
- Acceso total y sin restricciones a todas las funcionalidades del sistema.
- Puede gestionar cualquier usuario, incluyendo otros Administradores.
- Realiza tareas de mantenimiento y configuración a bajo nivel.
- Es el único rol que puede saltarse todas las comprobaciones de permisos.
