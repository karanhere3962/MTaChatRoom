import sys
import socket
import threading

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Manager(QObject):
    logSignal = pyqtSignal(str)
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = {}
        self.clientaddr = {}
        self.shutting = False
        self.encoding = 'utf8'
        self.buffsize = 2048

    def create_server(self, host, port):
        try:
            self.logSignal.emit("Creating server")
            print("Creating Server")
            self.s.bind((host, port))
            self.s.listen(10)
            print("Server Created")
            self.logSignal.emit("Server Created.")
            self.logSignal.emit("Started listening to clients")
            self.listen()
        except Exception as e:
            print(e)
            self.logSignal.emit("Error occured")

    def listen(self):
        try:
            print("started listenting")
            while self.shutting == False:
                client, addr = self.s.accept()
                self.address[client] = addr
                message = "Enter your name: "
                client.send(message.encode(self.encoding))
                threading.Thread(target =self.handleclient, args = (client,), daemon=True).start()
        except Exception as e:
            print('Error occured while creating server. ',e)

    def handleclient(self, client):
        try: 
            name = client.recv(self.buffsize).decode(self.encoding)
            self.logSignal.emit(name + " connected from address " + str(self.address[client]))
            self.clientaddr[client] = name
            message = "Welcome " + name + "!! You have entered the chatroom."
            client.send(message.encode(self.encoding))
            message = name + "has entered the chatroom. "
            self.broadcast(message, client)
            while self.shutting == False:
                data = client.recv(self.buffsize).decode(self.encoding)
                self.logSignal.emit(name + ': ' + data)
                self.broadcast(data, client)

        except Exception as e:
            del self.address[client]
            del self.clientaddr[client]
            self.logSignal.emit('Error occured while connecting to client. ' + str(e))
            message = name + " entered the chatroom."
            self.broadcast(message.encode(self.encoding), False)

    def broadcast(self, mesage, client):
        try:
            for sock in self.address.keys():
                if sock != client:
                    sock.send(message)
        except Exception as e:
            self.logSignal.emit("Error occured while broadcasting the message to clients. ", e)
            print(e)

    def stop(self):
        self.shutting = True
        self.s.close()

class sWindow(QMainWindow):
    def __init__(self, title = "File Sharing"):
        super().__init__()
        self.initUi()

        self.port = 15478
        self.manager = Manager()
        self.manager.logSignal.connect(self.display.append)

    def initUi(self):
        self.resize(800, 600)
        self.setWindowTitle("File Sharing")
        self.setWindowIcon(QIcon("fSharing.jpg"))
        self.setCentralWidget(QWidget(self))
        self.grid = QGridLayout(self.centralWidget())
        self.grid.setSpacing(10)
        self.setup()

    def setup(self):
        self.connect = QPushButton("Connect")
        self.connect.setToolTip("Connect to the server")
        self.connect.resize(self.connect.sizeHint())

        self.create = QPushButton("Create Server")
        self.create.setToolTip("Create server for others to connect")
        self.create.resize(self.create.sizeHint())
        self.chooseFile = QPushButton("Choose File")
        self.chooseFile.setToolTip("Choose the file you want to send.")
        self.chooseFile.setEnabled(False)
        self.chooseFile.resize(self.chooseFile.sizeHint())

        self.send = QPushButton("Send")
        self.send.setEnabled(False)
        self.send.resize(self.send.sizeHint())

        self.sendFile = QPushButton("Send File")
        self.sendFile.setToolTip("Send the selected file")
        self.sendFile.setEnabled(False)

        self.ip = QLineEdit()
        self.ip.setPlaceholderText("Ex: 192.168.0.1")

        self.display = QTextEdit()
        self.display.setReadOnly(True)

        self.sendText = QTextEdit()

        self.lbl = QLabel()
        self.lbl.setText(" Or ")

        self.grid.addWidget(self.create, 0,3 )
        self.grid.addWidget(self.lbl, 0,5)
        self.grid.addWidget(self.ip, 0,7)
        self.grid.addWidget(self.connect,0,9)
        self.grid.addWidget(self.display, 1, 1, 8, 7)
        self.grid.addWidget(self.chooseFile, 2, 9)
        self.grid.addWidget(self.sendFile, 4, 9)
        self.grid.addWidget(self.sendText, 9, 1, 2, 7)
        self.grid.addWidget(self.send, 9,9)
        self.centr()

        self.create.clicked.connect(self.on_create)

    def on_create(self):
        threading.Thread(target = self.manager.create_server, daemon=True, args = (self.ip.text(), self.port)).start()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Message Box", "Are you sure?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.manager.stop()
            event.accept()
        else:
            event.ignore()

    def centr(self):
        qr = self.frameGeometry()
        cr = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cr)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = sWindow()
    win.show()
    sys.exit(app.exec())