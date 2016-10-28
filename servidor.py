# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic 
from xmlrpc.server import SimpleXMLRPCServer
from random import randint

class Vibora():
	def __init__(self):	#init de prueba
		self.Id = randint(0, 1000000000)
		self.cuerpo = [(1, 0), (2, 0), (3, 0),  (4, 0),  (5, 0)]
		self.direccion = 0;
		self.color = {'b' : randint(0, 255), 'r' : randint(0, 255), 'g' : randint(0, 255)}
	
	def actualiza(self, table, col, fil):
		del self.cuerpo[0]
		lr, ud = self.cuerpo[3]
		if (self.direccion == 1  or self.direccion == 3):
			lr = ((1 if self.direccion == 1 else -1)+lr)%col
		else:
			ud = ((1 if self.direccion == 2 else -1)+ud)%fil
		self.cuerpo.append((lr, ud))

formClass , baseClass = uic.loadUiType("servidor.ui")

class ServidorApp(formClass, baseClass):
	def __init__(self, parent = None):
		formClass.__init__(self)
		baseClass.__init__(self)
		self.setupUi(self)
		self.juegoActivo = 0
		self.viboras = []
		self.timer = QtCore.QTimer()
		self.btn_terminar = QtGui.QPushButton('Terminar Juego')	#boton para terminar el juego
		self.table.horizontalHeader().setResizeMode(1)
		self.table.verticalHeader().setResizeMode(1)
		self.table.setFocusPolicy(0x3)
		
		#conectamos a los botones y mas a las funciones adecuadas.
		self.timer.setInterval(self.spinBox_Wait.value())
		self.spinBox_Columnas.valueChanged.connect(self.cambiarTam)
		self.spinBox_Filas.valueChanged.connect(self.cambiarTam)
		self.spinBox_Wait.valueChanged.connect(self.cambiarEspera)
		self.btn_Juego.clicked.connect(self.cambiaEstado)
		self.btn_Serv.clicked.connect(self.creaServidor)
		self.btn_terminar.clicked.connect(self.acabaJuego)
		self.timer.timeout.connect(self.mainloop)
		
		self.show()
	
	#Cambia la velocidad del juego
	def cambiarEspera(self):
		self.timer.setInterval(self.spinBox_Wait.value())
	
	#cambia el numero de colas y filas en la TableWidget
	def cambiarTam(self):
		self.table.setRowCount(self.spinBox_Filas.value())
		self.table.setColumnCount(self.spinBox_Columnas.value())
	
	#crea el servidor
	def creaServidor(self):
		self.server = SimpleXMLRPCServer((self.URL.text(), self.spinBox_Puerto.value()), 
                        allow_none=True)
		self.server.register_function(self.ping)
		self.server.register_function(self.yo_juego)
		self.server.register_function(self.cambia_direccion)
		self.server.register_function(self.estado_del_juego)
		self.server.timeout = self.spinBox_Timeout.value()
		if (self.spinBox_Puerto.value() == 0):
			self.spinBox_Puerto.setValue(self.server.server_address[1]);
	
	def ping(self):
		return "¡Pong!"
	
	#agrega una serpiente al juego
	def yo_juego(self):
		vib = Vibora()
		self.viboras.append(vib)
		return {"id": vib.Id, "color": vib.color}
	
	#cambia la direccion de la serpiente especificada
	def cambia_direccion(self, Id, nDir):
		for v in self.viboras:
			if(v.Id == Id):
				if (v.direccion != nDir-2 and v.direccion != nDir+2):
					v.direccion = nDir
	
	#regresea el estado del juego
	def estado_del_juego(self):
		infovib = []
		for v in self.viboras:
			infovib.append({"id": v.Id, "camino": v.cuerpo, "color": v.color})
		return {"espera": self.spinBox_Wait.value(),"tamX": self.spinBox_Columnas.value(), 
				"tamY": self.spinBox_Filas.value(), "viboras": infovib}
		
	#Cambia el estado del juego
	def cambiaEstado(self):
		if self.juegoActivo == 0:		#juego no ha comenzado
			self.btn_Juego.setText("Pausar el juego")
			self.juegoActivo = 1
			self.timer.start()
			self.btn_terminar.show()
			self.verticalLayout.addWidget(self.btn_terminar)
		elif self.juegoActivo == -1:	#juego esta en pausa
			self.btn_Juego.setText("Pausar el juego")
			self.juegoActivo = 1
			self.timer.start()
		else:							#juego esta activo
			self.btn_Juego.setText("Continuar el juego")
			self.juegoActivo = -1
			self.timer.stop()
	
	#Regresa todo al estado original
	def acabaJuego(self):
		self.juegoActivo = 0
		self.btn_Juego.setText("Inicia Juego")
		self.verticalLayout.removeWidget(self.btn_terminar)
		self.btn_terminar.hide()
		self.table.clear()
		self.viboras.clear()
		self.timer.stop()
	
	#dibuja las serpientes
	def dibuja(self):
		for v in self.viboras:
			for (x, y) in v.cuerpo:
				self.table.setItem(y, x, QtGui.QTableWidgetItem())
				self.table.item(y, x).setBackground(QtGui.QColor(v.color['r'], v.color['g'], v.color['b']))
		for v in self.viboras:
			for w in self.viboras:
				if v == w: 
					continue
				for i in range(1, len(w.cuerpo)):
					if v.cuerpo[0][0] == w.cuerpo[i][0] and v.cuerpo[0][1] == w.cuerpo[i][1]:	
						self.viboras.remove(w)
						del w
						break
	
	
	#actualiza las viboras
	def actualizaViboras(self):
		for v in self.viboras:
			v.actualiza(self.table, self.table.columnCount(),self.table.rowCount())
			
	#loop principal del juego
	def mainloop(self):
		if self.juegoActivo == 1:
			self.server.handle_request()
			self.table.clear()
			self.actualizaViboras()
			self.dibuja()


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	window = ServidorApp()
	sys.exit(app.exec_())
