"""
Proyecto Django de ConsultaVoto.

Usa PyMySQL como controlador de MySQL en lugar de mysqlclient. PyMySQL está
escrito solo en Python: el Control inteligente de aplicaciones de Windows 11
bloqueaba el componente compilado de mysqlclient, que no tiene firma digital.
Este paquete se importa antes que los settings, así que el registro aplica a
manage.py, al servidor y a pytest.
"""
import pymysql

pymysql.install_as_MySQLdb()
