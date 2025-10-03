import docker

"""
TODO:
- Рефакторинг
- Белые списки
- Сокет
- Capabilities
"""

client = docker.from_env()

def monitor_privileged_containers():
    print("Слушаю события Docker для обнаружения привилегированных контейнеров...")

    # Подписываемся на события контейнеров
    for event in client.events(decode=True, filters={'type': 'container'}):
        # События запуска контейнера
        if event['Action'] == 'start':
            container_id = event['id']
            try:
                # Получаем информацию о контейнере
                container = client.containers.get(container_id)
                inspect = container.attrs

                # Проверяем, является ли контейнер привилегированным
                if inspect['HostConfig']['Privileged']:
                    container.kill()
                    print(f"\n=== Обнаружен привилегированный контейнер ===")
                    print(f"ID: {container.id[:12]}")
                    print(f"Name: {container.name}")
                    print(f"Image: {container.image.tags[0] if container.image.tags else 'unknown'}")
                    print(f"Status: {container.status}")
                    print(f"Started at: {inspect['State']['StartedAt']}")
                    print(f"Command: {' '.join(inspect['Config']['Cmd']) if inspect['Config']['Cmd'] else 'N/A'}")
            except docker.errors.NotFound:
                # Контейнер мог уже завершиться
                print(f"Контейнер {container_id[:12]} был удалён до проверки.")
            except Exception as e:
                print(f"Ошибка при проверке контейнера {container_id[:12]}: {e}")

if __name__ == "__main__":
    try:
        monitor_privileged_containers()
    except KeyboardInterrupt:
        print("\nМониторинг остановлен.")