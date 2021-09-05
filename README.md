
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)


# Evaluacion Tinetti IA

Software creado para evaluar la marcha del paciente mediante la prueba Tinetti. Este software es el resultado final del TFM para el master en Ingeniería y Ciencia de Datos "Evaluación funcional de la marcha del adulto mayor mediante un sistema de sensorización inercial y técnicas de aprendizaje automático".

# Dependencias 

Para instalar las dependencias para usar el software:

````shell
pip install -r requirements.txt
````

# Instrucciones de uso 

````shell
run.py [-h] -f FILE [-n NAME] [-s SURNAME] [-a AGE] [-r REPORT] [-o OUTPUT]
````

- `-h`, `--help` Muestra la ayuda y finaliza la ejecución
- `-f FILE`, `--file FILE` Ruta del archivo xlxs exportado del software xsens 
- `-n NAME`, `--name NAME` Cadena de texto con el nombre del paciente
- `-s SURNAME`, `--surname SURNAME` Cadena de texto con el apellido del paciente (entre comillas)
- `-a AGE`, `--age AGE` Entero con la edad del paciente
- `-r REPORT`, `--report REPORT` Variable booleana (true por defecto) que indica si se quiere o no generar informe
- `-o OUTPUT`, `--output OUTPUT` Ruta en la que se quiere exportar el informe resultado (./report.pdf) por defecto

# Ejemplos de uso 

```shell
python run.py -f examples/record_1.xlsx -n "Nombre" -s "Apellido1 Apellido2" -a 24 
```

