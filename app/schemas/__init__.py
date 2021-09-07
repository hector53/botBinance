from datos import *
import pymysql
# datos Host para db
host = datos["host"]
database = datos["database"]
userDb = datos["userDb"]
userPass = datos["userPass"]
# datos Host para db

# consultas mysql

def getData(consulta):
    con = pymysql.connect(host=host,   user=userDb,
                          password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            cur.execute(consulta)
            rows = cur.fetchall()
            return rows

    finally:
        con.close()

def getDataOne(consulta):
    con = pymysql.connect(host=host,   user=userDb,
                          password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            cur.execute(consulta)
            rows = cur.fetchone()
            return rows

    finally:
        con.close()

# update o insert

def updateData(consulta):
    con = pymysql.connect(host=host,   user=userDb,
                          password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            guardar = cur.execute(consulta)
            con.commit()
            return guardar

    finally:
        con.close()

# consultas mysql fin


# mysql q me traigo del otro archivo me da pereza adaptarlas al nuevo
#esto viene del main , ya q se usa lo mismo, pero deberia adaptarlas a la nueva manera en que hago las consultas
#peero se q esto va cambiar completamente asi q mejor no pierdo tiempo en eso

def guardarTablaFuture(symbol, markPrice, indexPrice, days,  dir_rate, annual_rate, fecha):
    con = pymysql.connect(host=host,   user=userDb,
                          password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO tabla_futures(id, symbol, markPrice, indexPrice, days, dir_rate, annual_rate, fecha ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(
                consulta, ('null', symbol, markPrice, indexPrice, days, dir_rate, annual_rate, fecha))
            con.commit()
            return guardar

    finally:
        con.close()


def EliminarTablaFuture():
    con = pymysql.connect(host=host,   user=userDb,
                          password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'DELETE FROM tabla_futures'
            guardar = cur.execute(consulta)
            con.commit()
            return guardar

    finally:
        con.close()


def insertarOrdenCompra(symbol, orderId, cantidadM, cantidadE, typeS, side, precioM, comisionM, fecha):
    con = pymysql.connect(host=host,   user=userDb,
                          password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO orden_compra(id, symbol, orderId, cantidadM, cantidadE, type, side, precioM, comisionM, fecha) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(consulta, ('null', symbol, orderId,
                                  cantidadM, cantidadE, typeS, side, precioM, comisionM, fecha))
            con.commit()
            return guardar

    finally:
        con.close()


def guardarTransferencia(tranId, typeS, asset, amount, fecha):
    con = pymysql.connect(host=host,   user=userDb,
                          password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO transferencia(id, tranId, type, asset, amount, fecha) VALUES (%s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(
                consulta, ('null', tranId, typeS, asset, amount, fecha))
            con.commit()
            return guardar

    finally:
        con.close()


def guardarFutureOrden(orderID, symbol, clientOrderId, typeS, side, precioE, precioCS, cont, transferido, porcentaje, status, fecha):
    con = pymysql.connect(host=host,   user=userDb,
                          password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO orden_future(id, orderID, symbol, clientOrderId, type, side, precioE, precioCS, cont, transferido, porcentaje, status, fecha ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(consulta, ('null', orderID, symbol, clientOrderId, typeS,
                                  side, precioE, precioCS, cont, transferido, porcentaje, status, fecha))
            con.commit()
            return guardar

    finally:
        con.close()


def guardarVolumenTransferido(entrada, costo, restante, comision, id_orden, fecha):
    con = pymysql.connect(host=host,   user=userDb,
                          password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO volumenoperacion(id, entrada, costo, restante, comision,  id_orden, fecha ) VALUES (%s, %s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(
                consulta, ('null', entrada, costo, restante, comision,  id_orden, fecha))
            con.commit()
            return guardar

    finally:
        con.close()


# mysql q me traigo del otro archivo fin
