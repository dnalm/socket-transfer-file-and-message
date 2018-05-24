import json
import pickle
import socket
import threading
import sys
import os
import time


def send_message(target_ip, port, content):
    """
    send a message to target IP
    :param target_ip:  target IP(string), such as '192.168.5.36'
    :param port:  target port(string), such as 9950
    :param content:  message content, such as 'hello,world!'
    """
    ip_port = (target_ip, int(port))
    sk = socket.socket()
    sk.connect(ip_port)
    sk.send(bytes(content, 'utf8'))
    sk.close()


def send_file(target_ip, target_port, filename):
    """
    send a file to target IP
    :param target_ip: target IP(string), such as '192.168.5.36'
    :param target_port: target port(string), such as 9945
    :param filename: file path(string), such as 'c:/sample.jpg', '/home/app.rpm'
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
    except socket.error as msg:
        print(msg)
        sys.exit(1)

    s.recv(1024)
    while True:
        if os.path.isfile(filename):
            fhead = pickle.dumps([os.path.basename(filename), os.stat(filename).st_size])
            s.send(fhead)
            print('sending file: {0}'.format(filename))

            fp = open(filename, 'rb')
            while 1:
                data = fp.read(1024)
                if not data:
                    print('{0} file send over...'.format(filename))
                    break

                s.send(data)

        time.sleep(5)
        s.close()
        break


def listen_message(local_ip, local_port):
    """
    listen a local port for message
    :param local_ip: local IP(string), such as '192.168.5.36'
    :param local_port: receive port(string), such as 9950
    """
    try:
        print('listening messages')
        ip_port = (local_ip, local_port)
        sk = socket.socket()
        sk.bind(ip_port)
        sk.listen(5)
        while True:
            conn, addr = sk.accept()
            client_data = conn.recv(1024)

            print(str(client_data, 'utf8'), "from ", conn.getpeername()[0])

            conn.close()
    except :
        print("message listener error")


def listen_file(local_ip, local_port, save_position):
    """
    listen a local port for file
    :param local_ip: local_ip: local IP(string), such as '192.168.5.36'
    :param local_port: local_port: receive port(string), such as 9950
    :param save_position: file received will be saved in this path, such as '/root/receive'
    """
    try:
        print('listening files')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((local_ip, local_port))
        s.listen(10)
    except socket.error as msg:
        print('file listener error')
        print(msg)
        sys.exit(1)

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=receive_a_file, args=(conn, addr, save_position))
        t.start()


def receive_a_file(conn, addr, save_position):
    """
    receive a file from a connection
    :param conn: a returned value from accept()
    :param addr:a returned value from accept()
    :param save_position:file received will be saved in this path, such as '/root/receive'
    """
    conn.send('Hi, Welcome to the server!'.encode())

    while 1:

        buf = conn.recv(1024)
        if buf:
            filename, filesize = pickle.loads(buf)
            new_filename = os.path.join(save_position, str(filename).replace('\\x00', ''))

            recvd_size = 0
            fp = open(new_filename, 'wb')

            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = conn.recv(1024)
                    recvd_size += len(data)
                else:
                    data = conn.recv(filesize - recvd_size)
                    recvd_size = filesize

                fp.write(data)
            fp.close()
            print('received file {} from {}'.format(str(filename).replace('\\x00', ''), addr))
        conn.close()
        break


# help message
help_strs = ["usage:\n", "\tsend <ip> -m <message>\tsend a message to target IP\n",
             "\tsend <ip> -f <filename>\tsend a file to target IP\n", "\tquit\t quit this program safety", "\r"]


def main():
    """
    cli mothed
    """
    # get conf
    with open("config.json") as f_conf:
        conf = json.load(f_conf)

    # listen
    t1 = threading.Thread(target=listen_message, args=(conf["local_ip"], conf["receive_port"]["message"],))
    t1.start()
    t2 = threading.Thread(target=listen_file,
                          args=(conf["local_ip"], conf["receive_port"]["file"], conf["save_position"]))
    t2.start()

    print(*help_strs)

    while True:

        try:

            print(">>", end='')
            in_str = input()

            if in_str.replace(' ', '') == '':
                continue

            args = in_str.split(' ')

            if args.__len__() == 1 and args[0] == 'quit':
                os._exit(1)

            if args.__len__() < 4 and args[0] != "send" or args[2] not in ["-m", "-f"]:
                print(*help_strs)
                continue

            target_ip = args[1]
            context_or_filename = ""
            for i in args[3:]:
                context_or_filename = context_or_filename + i

            if args[2] == "-m":
                # send message
                t = threading.Thread(target=send_message,
                                     args=(target_ip, conf["receive_port"]["message"], context_or_filename,))
                t.start()
            elif args[2] == "-f":
                # send file
                t = threading.Thread(target=send_file,
                                     args=(target_ip, conf["receive_port"]["file"], context_or_filename,))
                t.start()
        except Exception as e:
            print("Error:", str(e))
            continue


if __name__ == '__main__':
    main()
