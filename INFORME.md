# Compose Generator

El script `generate_clients.py` genera automáticamente el archivo `docker-compose.yaml` para levantar la solución con un servidor y una cantidad variable de clientes. Recibe por línea de comandos el número de clientes a crear y construye la configuración de cada servicio con sus variables de entorno, dependencias y datos de build. Además, usa un `Dumper` personalizado de PyYAML para mantener un formato legible en el archivo generado. Si el parámetro no es válido, muestra un mensaje de uso.
