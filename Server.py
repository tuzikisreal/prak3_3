#!/usr/bin/env python3

import errno
import socket
from datetime import datetime
import json

default_port = "3212"
debagmode = False


def print_log(text):
    print(text)
    current_time = datetime.now().time()
    with open('log.txt', 'a', encoding='UTF-8') as file:
        file.write(f'[%d:%d:%d]: ' % (current_time.hour, current_time.minute, current_time.second) + text + '\n')


def try_port(port):
    tying_socket = None
    try:
        tying_socket = socket.socket()
        tying_socket.bind(("127.0.0.1", port))
        print_log("Запуск сервера на 127.0.0.1:" + str(port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            print_log("Порт " + str(port) + " уже используется, попытка принять следущий")
            return None
    return tying_socket


def init():
    port_found = False
    global default_port
    global debagmode
    while not port_found:
        if not debagmode:
            input_port = input(
                'Введите порт от 1024 до 65535, оставьте пустым для установления значения по умолчанию:' + default_port + ': ')
        else:
            input_port = default_port
        if input_port == "":
            input_port = default_port
        if input_port.isdigit() and 1024 <= int(input_port) <= 65535:
            port = int(input_port)
            new_socket = None
            while new_socket is None:
                new_socket = try_port(port)
                port += 1
            return new_socket
        else:
            print("Ошибка при вводе")


try:
    with open('db.json', 'r', encoding='utf-8') as f:
        reg_user = json.load(f)
except:
    reg_user = {}
    with open(f'db.json', 'w', encoding='utf-8') as f:
        json.dump(reg_user, f, ensure_ascii=False, indent=4)


my_socket = init()
stop_command_send = False
while stop_command_send is False:
    my_socket.listen(1)
    print_log("Прослушивания порта")
    conn, addr = my_socket.accept()
    print_log("Подключение клиента: " + addr[0] + ":" + str(addr[1]))
    user = addr[0]
    user_status = "unauthorized"
    while True:
        msg = ''
        if user_status == "unauthorized":
            if reg_user.get(user) is None:
                conn.send('Вы не зарегистрированы. Зарегистрируйтесь в формате: "Имя" "пароль"'.encode())
                data = conn.recv(1024)
                print_log("Прием данных от клиента " + addr[0] + ":" + str(addr[1]) + " : " + data.decode())
                if not data:
                    break
                msg = data.decode()
                print(msg)
                reg_user[user] = {}
                reg_user[user]["name"] = msg.split()[0]
                reg_user[user]["password"] = msg.split()[1]
                with open(f'db.json', 'w', encoding='utf-8') as f:
                    json.dump(reg_user, f, ensure_ascii=False, indent=4)
                conn.send(('Вы зарегистрировались, ' + reg_user[user]["name"] + ". Введите что вам переотправить").encode())
                user_status = "authorized"
            else:
                conn.send(('Здравствуйте, ' + reg_user[user]["name"] + ". Введите ваш пароль для продолжения:").encode())
                data = conn.recv(1024)
                print_log("Прием данных от клиента " + addr[0] + ":" + str(addr[1]) + " : " + data.decode())
                if not data:
                    break
                msg = data.decode()
                if reg_user[user]["password"] == msg:
                    conn.send(('Вы вошли, ' + reg_user[user]["name"] + ". Введите что вам переотправить").encode())
                    user_status = "authorized"
        else:
            data = conn.recv(1024)
            print_log("Прием данных от клиента " + addr[0] + ":" + str(addr[1]) + " : " + data.decode())
            if not data:
                break
            msg = data.decode()
            if msg == "exit":
                conn.send("exit".encode())
                break
            if msg == "stop server":
                conn.send("exit".encode())
                stop_command_send = True
                my_socket.close()
                print_log("Остановка сервера 127.0.0.1")
                break
            conn.send((msg*2).encode())
            print_log("Отправка данных клиенту" + addr[0] + ":" + str(addr[1]) + " : " + msg)
    print_log("Отключение клиента: " + addr[0] + ":" + str(addr[1]))

