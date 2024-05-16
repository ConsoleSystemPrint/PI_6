import socket
import ssl
import base64

class PI_6:
    def __init__(self, server, port, username, password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.sock = None

    def connect(self):
        try:
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=self.server)
            self.sock.connect((self.server, self.port))
            self._get_response()
        except socket.error as e:
            print(f"Ошибка подключения к серверу: {e}")
            raise

    def _send_command(self, command):
        self.sock.sendall((command + "\r\n").encode('utf-8'))

    def _get_response(self):
        response = b""
        while not response.endswith(b"\r\n"):
            response += self.sock.recv(1)
        return response.decode('utf-8')

    def login(self):
        self._send_command(f"USER {self.username}")
        response = self._get_response()
        if not response.startswith("+OK"):
            print(f"Ошибка при отправке имени пользователя: {response}")
            raise Exception("Ошибка входа")

        self._send_command(f"PASS {self.password}")
        response = self._get_response()
        if not response.startswith("+OK"):
            print(f"Ошибка при отправке пароля: {response}")
            raise Exception("Ошибка входа")

    def list_messages(self):
        self._send_command("LIST")
        response = self._get_response()
        if not response.startswith("+OK"):
            print(f"Сообщения со списком ошибок: {response}")
            raise Exception("Не удалось отобразить список сообщений")

        messages = []
        while True:
            line = self._get_response()
            if line == ".\r\n":
                break
            messages.append(line)
        return messages

    def retr_message(self, msg_number, lines=0):
        if lines > 0:
            command = f"TOP {msg_number} {lines}"
        else:
            command = f"RETR {msg_number}"

        self._send_command(command)
        response = self._get_response()
        if not response.startswith("+OK"):
            print(f"Сообщение об ошибке при получении сообщения: {response}")
            raise Exception("Не удалось получить сообщение")

        message = []
        while True:
            line = self._get_response()
            if line == ".\r\n":
                break
            message.append(line)
        return message

    def quit(self):
        self._send_command("QUIT")
        response = self._get_response()
        self.sock.close()
        return response

def main():
    server = "pop.gmail.com"
    port = 995
    username = "email@gmail.com"
    password = "password"

    client = PI_6(server, port, username, password)
    client.connect()
    client.login()

    messages = client.list_messages()
    print("Сообщения:\n", messages)

    if messages:
        msg_number = int(messages[0].split()[0])
        print(f"\nЗаголовки первых сообщений:\n", "".join(client.retr_message(msg_number, 0)))

        print("\nВсе содержимое первого сообщения:\n")
        message = client.retr_message(msg_number)
        for line in message:
            print(line, end='')

    client.quit()

if __name__ == "__main__":
    main()