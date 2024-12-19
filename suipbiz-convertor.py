import ipaddress
from typing import List, Tuple

def is_ipv6(ip_range: str) -> bool:
    """Проверяет, является ли диапазон IPv6."""
    try:
        start, end = ip_range.split('-')
        ipaddress.IPv6Address(start.strip())
        return True
    except:
        return False

def parse_ipv4_range(ip_range: str) -> Tuple[str, str]:
    """Разбивает строку диапазона IPv4 на начальный и конечный адрес."""
    start, end = ip_range.strip().split('-')
    return start.strip(), end.strip()

def expand_ip_range(start_ip: str, end_ip: str) -> List[str]:
    """Преобразует диапазон IP в список отдельных IP-адресов."""
    start = int(ipaddress.IPv4Address(start_ip))
    end = int(ipaddress.IPv4Address(end_ip))
    return [str(ipaddress.IPv4Address(ip)) for ip in range(start, end + 1)]

def process_ip_file(input_file: str, output_file: str):
    """Обрабатывает файл с IP-адресами."""
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    result = []
    for line in lines:
        # Пропускаем пустые строки
        if not line.strip():
            continue
            
        # Обрабатываем каждый диапазон IP в строке
        for ip_range in line.strip().split():
            if is_ipv6(ip_range):
                continue  # Пропускаем IPv6 адреса
                
            start_ip, end_ip = parse_ipv4_range(ip_range)
            expanded_ips = expand_ip_range(start_ip, end_ip)
            result.extend(expanded_ips)
    
    # Записываем результат в файл
    with open(output_file, 'w') as f:
        for ip in result:
            f.write(f"{ip}\n")

# Пример использования
if __name__ == "__main__":
    process_ip_file("Kyiv City-suip.biz.txt", "processed-addresses.txt")