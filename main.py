import docker

from services.dockerMonitoringService import DockerMonitorService

"""
TODO:
- Рефакторинг
- Белые списки
- Сокет
- Capabilities
- Логи
"""

client = docker.from_env()
dockerMonitoringService = DockerMonitorService(client)


if __name__ == "__main__":
    try:
        dockerMonitoringService.monitor_containers()
    except KeyboardInterrupt:
        print("\nМониторинг остановлен.")