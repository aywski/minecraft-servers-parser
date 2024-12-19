import csv
import asyncio
import re
from mcstatus import JavaServer

# Чтение IP-адресов из файла с возможностью сканирования диапазона строк
def read_ips_from_file(filename, start_line=0, end_line=None):
    with open(filename, 'r') as file:
        ips = file.readlines()
        # Ограничиваем диапазон строк, если указаны start_line и end_line
        return [ip.strip() for ip in ips[start_line:end_line]] if end_line else [ip.strip() for ip in ips[start_line:]]

# Сохранение информации в CSV
def save_to_csv(ip, players, server_name, version, filename="active_minecraft_servers.csv"):
    # Проверяем, существует ли файл и пуст ли он
    file_exists = False
    try:
        with open(filename, 'r') as file:
            file_exists = True
            # Проверяем, не пуст ли файл
            if not file.read():
                file_exists = False
    except FileNotFoundError:
        pass

    # Записываем данные в CSV
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Если файл пустой, добавляем заголовки
            writer.writerow(["IP Address", "Online Players", "Version", "Server Name"])
        writer.writerow([ip, players, server_name, version])

# Обработка названия сервера
def clean_server_name(server_name):
    # Удаляем все непечатаемые символы и лишние пробелы
    server_name = re.sub(r'[^\x00-\x7F]+', '', server_name)  # Удаляем не ASCII символы
    server_name = server_name.strip()  # Удаляем пробелы в начале и в конце
    return server_name

# Асинхронная функция для проверки статуса сервера
async def check_server(ip, semaphore):
    async with semaphore:
        try:
            server = JavaServer.lookup(ip)
            status = await server.async_status()  
            server_name = clean_server_name(status.description)  # Очищаем название сервера
            save_to_csv(ip, status.players.online, status.version.name, server_name)
            print(f"Server found! Version: {status.version.name}, IP: {ip}, Players: {status.players.online}")

            return True, ip, status.players.online, status.version.name, server_name
        except Exception:
            return False, ip, 0, "", ""  # Если сервер недоступен

# Основная асинхронная функция для параллельной проверки серверов
async def check_all_servers(ips, max_concurrent_requests):
    try:
        semaphore = asyncio.Semaphore(max_concurrent_requests)
        tasks = [check_server(ip, semaphore) for ip in ips]
        await asyncio.gather(*tasks)
    except Exception:
        print("something went wrong in check_all_servers()")

# Основная логика
async def main():
    max_concurrent_requests = 500
    # Запрос диапазона строк
    start_line = 200000
    end_line = 400000
    input_file = "processed-addresses.txt"

    end_line = int(end_line) if end_line else None
    ips = read_ips_from_file(input_file, start_line, end_line)

    await check_all_servers(ips, max_concurrent_requests)  # Проверка всех серверов
    print("Активные серверы сохранены в active_minecraft_servers.csv")

# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())
