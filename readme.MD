# Análisis Calidad de la Gasolina - República Dominicana

Este repositorio contiene los archivos resultantes del análisis de la calidad de los combustibles por medio del octanaje, calculado tanto por el método RON como por el método MON. El análisis se limita a los combustibles de tipo premium y regular y se usan técnicas descriptivas y gráficas para el desarrollo de este.

# Librerías Usadas

Para este análisis se usaron varias librerías, entre las que se destacan Pandas, Matplotlib, Pypdf, OCRMyPDF, entre otras. Todas las librerías usadas se encuentran en el archivo 'requirements.txt' de este repositorio.

# Método de Extracción de Datos

Los datos usados para el análisis fueron tomados directamente de los reportes disponibles en la página web del Ministerio de Industria y Comercio - MICM. Estos reportes fueron colgados escaneados, por lo que la extracción del texto para el análisis se dificulta.

Por tanto, se procedió a procesar cada uno de los reportes por medio de la librería OCRMyPDF, la cual realiza un reconocimiento óptico de los caracteres. Posterior a esto, se eliminaron las páginas que no formaron parte del alcance del análisis.

Como segundo paso, se utilizó el servicio de Azure Document Intelligence para reconocer las tablas y extraer las columnas y filas de datos. De 800 archivos aproximadamente, un total de 99 no pudieron ser procesados. Queda pendiente revisar las razones por las cuales estos 99 archivos dieron error.

Por último, se procedió a realizar una revisión manual de los datos extraídos por medio de Azure con el contenido original de los reportes, para confirmar que los datos son correctos. Se determinó una muestra aleatoria de 32 archivos por medio de la tabla ANSI Z1.4, usando el tipo de inspección General I y un AQL de 0.4. Aún está pendiente por concluir la revisión, pero hasta el momento los datos extraidos coinciden con el contenido de los informes.

## Análisis de los Datos

El análisis de los datos utilizó cerca de 700 archivos como fuente de información. El análisis se realizó por medio de la librería Pandas. En este repositorio se puede encontrar un reporte en formato PDF como también en HTML.

## Licencia

 Toda la información de este repositorio está disponible de forma abierta y puede ser usada por cualquier persona interesada. Solo pido que por favor no olvides dar los créditos si vas a usar estos resultados para algún trabajo, informe, etc. 😎
```
@MISC{RMATEO2024,
  AUTHOR = {Rafael J. Mateo},
  TITLE  = {Análisis Calidad de Combustibles - Rep. Dom.[Reporte]},
  YEAR   = {2024},
  URL    = {https://github.com/rafaeljosem/gas_station_analysis}
}
```