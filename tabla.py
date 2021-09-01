from binance.client import Client
from binance.exceptions import BinanceAPIException
from datetime import datetime, date
import pymysql

import time

#api binance
api_key='gaszgeLW551gSiwYpqxJCbsdO2bLeD7yXbPIj9avbdM7H1pivsSVr7pPr5SaQz4W'
api_secret='6SV2XS5aiwWMUZDaj24P7iaAWVJLZOOL3i8jMsYDXlCx0VY7EDrNUbZZJSVf1yx8'
#finapibinance

#datos Host para db
host="localhost"
database="pythontest"
userDb = "root"
userPass=""
#datos Host para db

#init binance api
client =   Client(api_key, api_secret)

def guardarTablaFuture(symbol, markPrice, indexPrice, days,  dir_rate, annual_rate, fecha):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO tabla_futures(id, symbol, markPrice, indexPrice, days, dir_rate, annual_rate, fecha ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(consulta, ('null', symbol, markPrice, indexPrice, days, dir_rate, annual_rate, fecha))
            con.commit()
            return guardar
            
    finally:
        con.close()

def EliminarTablaFuture():
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'DELETE FROM tabla_futures'
            guardar = cur.execute(consulta)
            con.commit()
            return guardar
            
    finally:
        con.close()

def calcularDias(symbol):
    txt = symbol
    x = txt.split("_")
    x = x[1]
    today = date.today()
    today = datetime.strptime(str(today), '%Y-%m-%d')
    fechaContrato = str(today.year)+"-"+str(x[2:4])+"-"+str(x[4:6])
    fechaContrato = datetime.strptime(fechaContrato, '%Y-%m-%d')
    remaining_days = (fechaContrato - today).days
    return remaining_days

def manual():
    dis = client.futures_coin_mark_price()
    EliminarTablaFuture()
    rango= range(len(dis))
    for n in rango:
        result = dis[n]["symbol"].find('2')
        if result != -1:
            dir_rate=float(dis[n]["markPrice"]) / float(dis[n]["indexPrice"] ) *100 - 100
            diasFaltantes = calcularDias(dis[n]["symbol"])
            annual_rate = dir_rate * 365 / diasFaltantes
            guardarTablaFuture(dis[n]["symbol"], dis[n]["markPrice"], dis[n]["indexPrice"], diasFaltantes,  str(dir_rate) ,  annual_rate,   datetime.now())



def ejecutarScript():
    try:
        resultado = manual()
    except:
        print("Hay un error en los valores de entrada")
    
    time.sleep(60)
""""
while True:
    ejecutarScript()
"""

getOrden = client.futures_coin_get_order(symbol='DOTUSD_210924', orderId='263501944')
print(getOrden)