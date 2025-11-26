# E-commerce Delivery Route Optimization System

## Descripción del Proyecto
Proyecto enfocado en optimizar operaciones de entrega en comercio electrónico ante el crecimiento proyectado del 12% en ventas en línea para 2024. Mediante técnicas de optimización estocástica, se desarrolló un sistema que determina las rutas de vehículos más eficientes y la asignación adecuada de recursos para entregas en 344 ubicaciones en Monterrey, México.

## Logros Clave
- Implementación del Problema de Rutas de Vehículos (VRP) con restricciones de capacidad y tiempo para minimizar distancia y tiempo de entrega.  
- Desarrollo de un sistema de simulación Monte Carlo que procesó más de 31,000 compras y 53,000 productos.  
- Evaluación de múltiples configuraciones de recursos mediante 100 iteraciones de simulación con 100 clientes cada una.  
- Identificación de la configuración óptima (3 vehículos + 1 andén de carga) que permitió completar entregas en un solo día.  
- Creación de un algoritmo de búsqueda greedy utilizando la librería simpleai para generar rutas de entrega eficientes.

## Detalles Técnicos
El proyecto se basó en análisis de frecuencia de datos históricos de pedidos para simular patrones de compra realistas. Se desarrolló un modelo matemático que integró matrices de distancia, restricciones de tiempo, capacidades vehiculares y eficiencia del andén de carga. El sistema generó horarios y rutas de entrega precisos respetando limitaciones operativas como capacidad máxima y horas de trabajo del personal.

## Impacto
El sistema de optimización permite a negocios de e-commerce planificar entregas con mayor eficiencia, reduciendo costos operativos y mejorando la satisfacción del cliente mediante tiempos de entrega más rápidos. Los resultados muestran que la configuración óptima (3 vehículos y 1 andén de carga) permite completar todas las entregas en un solo día con mínima capacidad ociosa, aportando información valiosa para la planificación logística.
