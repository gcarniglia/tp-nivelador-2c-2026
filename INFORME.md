# INFORME

## EJERCICIO 1: Compose Generator

El script `generate_clients.py` genera automáticamente el archivo `docker-compose.yaml` para levantar la solución con un servidor y una cantidad variable de clientes. Recibe por línea de comandos el número de clientes a crear y construye la configuración de cada servicio con sus variables de entorno, dependencias y datos de build. Además, usa un `Dumper` personalizado de PyYAML para mantener un formato legible en el archivo generado. Si el parámetro no es válido, muestra un mensaje de uso.

## EJERCICIO 2: test_server.sh

Se definió una red en el `docker-compose.yaml` con el nombre de `gabynet`. Dicha red permite conexiones externas a la misma y permite conectar manualmente otros contenedores. El nuevo script `test_server.sh` crea un contenedor con imagen Alpine "efímero" (--rm), conectado a la red `gabynet`, que envía al echo server "Hola Mundo" a través del puerto interno 5678, con timeout de 2 segundos.

Nota: El anterior script `generate_clients.py` fue actualizado para soportar los nuevos cambios de networking.
