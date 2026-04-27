# Media Catalog Analyzer

App para comparar proveedores de medios (Publisuites, Getalink, etc.) con análisis de métricas e insights con IA.

## Instalación local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Uso

1. Sube uno o más CSVs desde el panel lateral
2. El nombre del archivo se usa como nombre del proveedor (ej: `publisuites_medios.csv` → proveedor "publisuites")
3. Filtra por proveedor, DA, precio o temática
4. Explora las pestañas: Comparativa, Precio vs Calidad, Distribución, Tabla
5. Añade tu API Key de Anthropic para generar insights automáticos con IA

## Formato CSV esperado

```
URL,Descripción,País,Idioma,Temática,DA,PA,DR,CF,TF,Tráfico web/mes,Precio
```

## Despliegue en Streamlit Cloud (para el equipo)

1. Sube este proyecto a GitHub
2. Ve a https://streamlit.io/cloud
3. Conecta tu repo y despliega
4. Comparte la URL con el equipo
