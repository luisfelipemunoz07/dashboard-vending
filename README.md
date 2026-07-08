# 📊 Dashboard de Ventas — Room 24.7

> Dashboard interactivo construido con Streamlit para analizar el historial
> de ventas de una máquina vending, permitiendo filtrar por producto y
> rango de fechas para tomar decisiones de negocio en tiempo real.

### 🌐 [Ver app en vivo →](https://dashboard-vending-njufxuhbt4p7l3g2toft2x.streamlit.app/)

---

## 🎯 Problema

El negocio necesitaba una forma visual y rápida de responder preguntas como:
- ¿Cuánto vendí de X producto en un periodo específico?
- ¿Cuál es mi margen de utilidad real por producto?
- ¿En qué días, semanas o meses vendo más?

Sin una herramienta así, el análisis se hacía manualmente en Excel,
lento y propenso a errores.

---

## ✨ ¿Qué hace el dashboard?

El usuario sube su archivo Excel y el dashboard automáticamente:

- 📁 **Limpia y procesa** los datos sin intervención manual
- 🔍 **Filtra** por producto y rango de fechas desde el sidebar
- 📦 **Muestra 4 métricas clave** en tiempo real:
  - Unidades totales vendidas
  - Ventas totales ($)
  - Utilidad generada ($)
  - Margen de utilidad (%)
- 📈 **Histórico diario** de unidades vendidas por producto
- 📊 **Promedios semanales y mensuales** con gráficas de barras

---

## 🖥️ Vista previa

<img width="1757" height="892" alt="image" src="https://github.com/user-attachments/assets/95227d75-2524-4b3b-b2f4-ea642bb32bae" />


*Análisis de BARRITAS PIÑA: 50 unidades · $1,000 en ventas · 61.9% de margen*

---

## 🌐 Demo en vivo

👉 **[Abrir dashboard](https://dashboard-vending-njufxuhbt4p7l3g2toft2x.streamlit.app/)**

> Sube cualquier archivo Excel con el formato indicado y el dashboard
> carga, limpia y visualiza tus datos automáticamente. No requiere
> instalación ni conocimientos técnicos.

---

## 🚀 ¿Cómo correrlo localmente?

**1. Clona el repositorio**
```bash
git clone https://github.com/luisfelipemunoz07/dashboard-vending.git
cd dashboard-vending
```

**2. Instala las dependencias**
```bash
pip install streamlit pandas matplotlib openpyxl
```

**3. Corre la app**
```bash
streamlit run app.py
```

**4. Formato del archivo Excel**

El archivo debe contener una hoja llamada
`HOJA PARA TABLA DINÁMICA` con estas columnas:

| Columna | Descripción |
|---|---|
| `FECHA` | Fecha de la venta |
| `PRODUCTO` | Nombre del producto |
| `CATEGORIA` | Categoría del producto |
| `VENTA UNIDADES` | Unidades vendidas |
| `VENTA $` | Ingreso en pesos |
| `UTILIDAD $` | Utilidad generada |

---

## 🛠️ Stack técnico

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=matplotlib&logoColor=white)

| Librería | Uso |
|---|---|
| `Streamlit` | Interfaz web interactiva con sidebar de filtros |
| `Pandas` | Carga, limpieza y transformación de datos |
| `Matplotlib` | Gráficas de histórico diario, semanal y mensual |
| `OpenPyXL` | Lectura de archivos Excel |

---

## 💡 Lo que aprendí

1. **Streamlit convierte Python en una app web en minutos** — ideal para
prototipos de dashboards sin necesidad de frontend.
2. **La limpieza de datos en tiempo real es un reto** — manejar fechas
corruptas, columnas vacías y tipos mixtos directamente desde un Excel
del usuario requiere validaciones robustas.
3. **El caché importa** — usar `@st.cache_data` hace la diferencia en
rendimiento cuando el archivo Excel es grande.

---

## 📬 Contacto

**Luis Felipe Muñoz**
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/luismunozmartinez/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/luisfelipemunoz07)
