# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui, uic 
from xmlrpc.client import ServerProxy


formClass , baseClass = uic.loadUiType("cliente.ui")

class ClienteApp(formClass, baseClass):
	def __init__(self):
		formClass.__init__(self)
		baseClass.__init__(self)
		self.proxy = None
		self.setupUi(self)
		self.timer = QtCore.QTimer()
		self.table.horizontalHeader().setResizeMode(1)
		self.table.verticalHeader().setResizeMode(1)
		self.table.setFocusPolicy(0x3)
		self.table.keyPressEvent = self.mandaAccion	#sobreescritura de metodo
		
		self.btn_Ping.clicked.connect(self.presionaPing)
		self.btn_Participar.clicked.connect(self.participar)
		self.show()
	
	def presionaPing(self):
		self.timer.timeout.connect(self.actualiza)
		self.btn_Ping.setText("Pinging")
		self.proxy = ServerProxy("http://"+self.URL.text()+":"+str(self.spinBox_Puerto.value()))
		self.btn_Ping.setText(self.proxy.ping())
		
	def participar(self):
		if self.proxy == None: return
		self.timer.start()
		datav = self.proxy.yo_juego()
		self.text_Id.setText(str(datav["id"]))
		r, g, b = str(datav["color"]['r']), str(datav["color"]['g']), str(datav["color"]['b'])
		self.text_Color.setStyleSheet("QLineEdit#text_Color { background-color: rgb("+r+", "+g+", "+b+") }")
	
	def mandaAccion(self, event):
		if self.proxy == None: return
		ident = int(self.text_Id.text())
		if event.key() == QtCore.Qt.Key_Up:
			self.proxy.cambia_direccion(ident, 0)
		elif event.key() == QtCore.Qt.Key_Down:
			self.proxy.cambia_direccion(ident, 2)
		elif event.key() == QtCore.Qt.Key_Left:
			self.proxy.cambia_direccion(ident, 3)
		elif event.key() == QtCore.Qt.Key_Right:
			self.proxy.cambia_direccion(ident, 1)
		
	def actualiza(self):
		self.table.clear()
		datos = self.proxy.estado_del_juego()
		self.timer.setInterval(datos["espera"]4)
		self.table.setRowCount(datos["tamY"])
		self.table.setColumnCount(datos["tamX"])
		for v in datos["viboras"]:
			for (x, y) in v["camino"]:
				if self.table.item(y, x) == None:	#si cae en una celda llena se elimina, si no, entonces se llena.
					self.table.setItem(y, x, QtGui.QTableWidgetItem())
					self.table.item(y, x).setBackground(QtGui.QColor(v["color"]['r'], v["color"]['g'], v["color"]['b']))
					
		
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	window = ClienteApp()
	sys.exit(app.exec_())
