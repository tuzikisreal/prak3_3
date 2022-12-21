#!/usr/bin/env python3

import socket

default_port = "3212"
default_ip = "127.0.0.1"
debagmode = False


def get_ip_port():
    ip_found = False
    port_found = False
    global default_port
    global default_ip
    global debagmode
    input_ip = ''
    while not ip_found:
        if not debagmode:
            input_ip = input(
                'Введите ip, оставьте пустым для установления значения по умолчанию:' + default_ip + ': ')
        else:
            input_ip = default_ip
        if input_ip == "":
            input_ip = default_ip
        splitted_ip = input_ip.split(".")
        if len(splitted_ip) != 4:
            print("Ошибка при вводе")
            continue
        for i in splitted_ip:
            if not i.isdigit() or 0 > int(i) or int(i) > 255:
                print("Ошибка при вводе")
                continue
        ip_found = True
        print("Ip введен")
    input_port = ''
    while not port_found:
        if not debagmode:
            input_port = input(
                'Введите порт от 1024 до 65535, оставьте пустым для установления значения по умолчанию:' + default_port + ': ')
        if input_port == "":
            input_port = default_port
        if input_port.isdigit() and 1024 <= int(input_port) <= 65535:
            input_port = int(input_port)
            port_found = True
        else:
            print("Ошибка при вводе")
    return input_ip, input_port


ip, port = get_ip_port()
sock = socket.socket()
sock.setblocking(1)
sock.connect((ip, port))
print("Соединение с сервером: " + ip + ":" + str(port))
while True:
    data = sock.recv(1024)
    print("Прием данных от сервера " + ip + ":" + str(port) + " : " + data.decode())
    if data.decode() == 'exit':
        sock.close()
        print("Разрыв соединения с сервером: " + ip + ":" + str(port))
        break
    msg = input()
    sock.send(msg.encode())
    print("Отправка данных серверу " + ip + ":" + str(port) + " : " + msg)
    exit_check = msg.lower()
