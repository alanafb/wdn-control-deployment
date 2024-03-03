# wdn-control-deployment

Repositorio con código para diseñar una red SCADA verificada mediante el algoritmo de Semántica Relacional Ternaria en una WDN, la cual permita optimizar la detección de un evento de contaminación del agua en la red 

## Requisitos previos

Es recomendable contar con una instalación de Anaconda y usar Spyder para ejecutar el código.

Se debe contar con un fichero de descripción de la WDN en la que queremos implantar el SCADA en formato .INP (archivo de entrada EPANET). 

Se debe conocer el número de elementos que deseamos situar en la red SCADA. En caso de no saberlo, se realizará una primera ejecución con un número arbitrario. Como resultado de la ejecución, se generará una gráfica que enfrenta el número de sensores presentes en la red frente al tiempo de detección de un evento de contaminación. Elegir en función de requisitos deseados.

## Instalación

Este proyecto se nutre de la biblioteca chama. Los pasos para su instalación figuran en el siguiente enlace: https://chama.readthedocs.io/en/latest/installation.html

Las dependencias del proyecto se resumen en las siguientes instalaciones:

```bash
pip install wntr
pip install numpy
pip install pandas
pip install matplotlib
pip install chama
pip install networkx
```

## Estructura del proyecto

El script principal a ejecutar es main.py. El resto de scripts son auxiliares para ayudar a la ejecución:

```
.
├── distancia_euclidea.py
├── main.py
├── modulo_chama.py
├── network_node_distance.py
├── node.py
└── prim_algorithm.py
```

Resulta útil manipular modulo_chama.py para modificar variables decisivas para el cálculo de ubicaciones de sensores. Consultar https://chama.readthedocs.io/en/latest/index.html.

## Uso

Para ejecutar el proyecto, se recomienda ejecutar el archivo main.py desde un IDE como Spyder. Se piden 4 argumentos de entrada:

    *Ruta del archivo .INP: Se escribirá la ruta absoluta al fichero
    *Número de sensores para el SCADA: Entero con el número de elementos de la red a diseñar
    *Tipo de enlace: Se escribirá 1 para enlaces por cable, basados en saltos de red, 2 para enlaces inalámbricos, basados en distancia euclídea, y 3 para poder seleccionar el tipo de enlace en cada conexión
    *Número de sensores para ampliar la red: Se escribirá un entero que represente con cuántos sensores se querría expandir la red SCADA generada

Se generará una serie de gráficos con los esquemas de nodos y conexiones del SCADA. Hay tres tipos de elementos: 

    *SCADA: Se visualiza en color rojo. Es el nodo 0 de la red. Si se quiere insertar un SCADA manualmente, se deberá descomentar en modulo_chama.py la siguiente línea: 
        selected_sensors.insert(0, {nombre_del_nodo_en_WDN}) 
    *PLC: Se visualizan en color verde. Todo nodo vecino del SCADA debe serlo
    *sensor: Se visualizan en color azul

Cada nodo tendrá su etiqueta de nodo, correspondiente con la que tiene configurada en el archivo .INP de descripción de la WDN.

## Licencia

Este código ha sido desarrollado como Trabajo Fin de Máster de la Escuela Técnica Superior de Ingenieros de Telecomunicación, de la Universidad Politécnica de Madrid. 

## Contacto

Para contactar sobre asuntos relacionados con el código, contactar a alana.fbasquero@alumnos.upm.es
