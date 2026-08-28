import yaml
import sys

SERVER_INTERNAL_PORT = 5678  # Puerto interno del servidor para la comunicación con los clientes.
SERVER_EXTERNAL_PORT = 5678  # Puerto externo del servidor para exponerlo fuera del contenedor.
INPUT_DIRECTORY = "/var/opt/input"
OUTPUT_DIRECTORY = "/var/opt/output"
INPUT_FILE = INPUT_DIRECTORY + "/input-*.csv"
OUTPUT_FILE = OUTPUT_DIRECTORY + "/output-*.csv"

class CustomDumper(yaml.Dumper):
    """Dumper de PyYAML con saltos extra para dejar el compose más legible."""

    def write_line_break(self, data=None):
        '''Escribe un salto de línea y añade un salto extra si estamos en la sangría principal de los servicios.'''
        super().write_line_break(data)
        if len(self.indents) == 1:
            super().write_line_break()

    def increase_indent(self, flow=False, indentless=False):
        """Fuerza la indentación de secuencias en bloque para mantener el formato esperado."""
        return super(CustomDumper, self).increase_indent(flow, indentless=False)

def generar_compose(numero_clientes):
    """Genera docker-compose.yaml con un servidor y la cantidad indicada de clientes."""

    compose_data = {
        "services": {
            "server": {
                "build": {
                    "context": "./services/server",
                    "dockerfile": "Dockerfile",
                },
                "container_name": "server",
                "environment": [
                    "PYTHONUNBUFFERED=1",
                    "SERVER_HOST=server",
                    f"SERVER_PORT={SERVER_INTERNAL_PORT}",
                ],
                "ports": [
                    f"{SERVER_EXTERNAL_PORT}:{SERVER_INTERNAL_PORT}"
                ],
                "networks": ["gabynet"]
            },
        }
    }
    for i in range(0, numero_clientes):
        compose_data["services"][f"client_{i}"] = {
            "build": {
                "context": "./services/client",
                "dockerfile": "Dockerfile",
            },
            "container_name": f"client_{i}",
            "depends_on": ["server"],
            "environment": [
                f"AGENCY_ID={i}",
                "SERVER_HOST=server",
                f"SERVER_PORT={SERVER_INTERNAL_PORT}",
                f"INPUT_FILE={INPUT_FILE.replace('*', str(i))}",
                f"OUTPUT_FILE={OUTPUT_FILE.replace('*', str(i))}"
            ],
            "networks": ["gabynet"],
            "volumes": [
                f"./input:{INPUT_DIRECTORY}:ro",
                f"./output:{OUTPUT_DIRECTORY}:rw"
            ]
        }
    compose_data["networks"] = {
        "gabynet": {
            "driver": "bridge",
            "name": "gabynet",
            "internal": False,
            "attachable": True,
            "ipam": {
                "config": [
                    {
                        "subnet": "172.11.0.0/16"
                    }
                ]
            }
        }
    }
    
    with open("docker-compose.yaml", "w") as file:
        yaml.dump(compose_data, file, Dumper=CustomDumper, default_flow_style=False, sort_keys=False)
        
    print(f"✅ Archivo docker-compose.yaml generado con éxito para {numero_clientes} cliente{('s' if numero_clientes > 1 else '')}.")

if __name__ == "__main__":
    # Valida el argumento CLI y dispara la generación del archivo compose.
    if len(sys.argv) > 1 and sys.argv[1].isnumeric() and int(sys.argv[1]) > 0:
        generar_compose(int(sys.argv[1]))
    else:
        print("❌ Uso: python generate_clients.py <numero_de_clientes>")