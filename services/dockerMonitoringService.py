import docker

"""
TODO:
- Рефакторинг
- Проектные TODO
"""


class DockerMonitorService:
    client = None

    def __init__(self, client):
        self.client = client

    def monitor_containers(self):
        print("Слушаю события Docker для обнаружения привилегированных контейнеров...")

        # Подписываемся на события контейнеров
        for event in self.client.events(decode=True, filters={'type': 'container'}):
            check = self.__check_event(event)
            if check[0] == True:
                self.__print_monitor_info(check[1], check[2])
            else:
                if len(check) > 1:
                    print(f"Контейнер : {check[1].name} непривилегированный")

    def __check_event(self, event):
        # События запуска контейнера
        if event['Action'] == 'start':
            container_id = event['id']

            try:
                # Получаем информацию о контейнере
                container = self.client.containers.get(container_id)

                try:
                    container.pause()
                    print(f"Контейнер '{container.name}' (ID: {container.id[:12]}) остановлен. Идёт проверка.")
                except docker.errors.APIError as e:
                    print(f"Ошибка остановки контейнера: {e}")

                inspect = container.attrs
                # Проверяем, является ли контейнер привилегированным
                if inspect['HostConfig']['Privileged']:
                    try:
                        container.kill()
                    except docker.errors.APIError as e:
                        print(f"Ошибка завершения контейнера: {e}")
                    return [True, container,inspect]
                else:
                    try:
                        container.unpause()
                        print(f"Контейнер '{container.name}' (ID: {container.id[:12]}) возобновлён.")
                    except docker.errors.APIError as e:
                        print(f"Ошибка возобновления контейнера: {e}")
                    return [False, container, inspect]

            except docker.errors.NotFound:
                # Контейнер мог уже завершиться
                print(f"Контейнер {container_id[:12]} был удалён до проверки.")
            except Exception as e:
                print(f"Ошибка при проверке контейнера {container_id[:12]}: {e}")
        else:
            return [False]

    def __print_monitor_info(self, container, inspect):
        print(f"\n=== Обнаружен привилегированный контейнер ===")
        print(f"ID: {container.id[:12]}")
        print(f"Name: {container.name}")
        print(f"Image: {container.image.tags[0] if container.image.tags else 'unknown'}")
        print(f"Status: {container.status}")
        print(f"Started at: {inspect['State']['StartedAt']}")
        print(f"Command: {' '.join(inspect['Config']['Cmd']) if inspect['Config']['Cmd'] else 'N/A'}")