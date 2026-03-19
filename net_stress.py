import socket
import time

# Настройки
TARGET_IP = "127.0.0.1"
TARGET_PORT = 5000
CONNECTIONS = 60 # Больше порога в 50

sockets = []

print(f"Открытие {CONNECTIONS} соединений с {TARGET_IP}:{TARGET_PORT}...")

for i in range(CONNECTIONS):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TARGET_IP, TARGET_PORT))
        sockets.append(s)
        if (i+1) % 10 == 0:
            print(f"Установлено {i+1} соединений...")
    except Exception as e:
        print(f"Ошибка на соединении {i+1}: {e}")

print("\n[!] Соединения открыты. Проверьте вкладку 'СЕТЬ' в дашборде.")
print("[!] На вкладке 'ОБЗОР' индекс защиты должен упасть, а статус измениться на WARNING.")
print("Нажмите Ctrl+C, чтобы закрыть соединения.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nЗакрытие соединений...")
    for s in sockets:
        s.close()
