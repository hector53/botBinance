import pymysql
import math
import time
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException

from datos import *  
#api binance
api_key=datos["api_key"]
api_secret=datos["api_secret"]
#finapibinance

#datos Host para db
host=datos["host"]
database=datos["database"]
userDb = datos["userDb"]
userPass=datos["userPass"]

#init binance api
client =   Client(api_key, api_secret)


#funciones 
def searchAssetinAccount(orden, b):
    rango= range(len(orden))
    index = 0
    for n in rango:
        if orden[n]["asset"] == b:
            index = n
    return index

#consultas mysql
def updateData(consulta):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            guardar = cur.execute(consulta)
            con.commit()
            return guardar
            
    finally:
        con.close()


def consultarWhere():
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM orden_form where realizada = 0')
            rows = cur.fetchall()
            return rows
            
    finally:
        con.close()

def updateOrdenForm(id_orden):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'update orden_form set realizada = 1 where id = %s;'
            guardar = cur.execute(consulta, (id_orden))
            con.commit()
            return guardar
            
    finally:
        con.close()

def guardarFutureOrden(orderID, symbol, clientOrderId, typeS, side, precioE, precioCS, cont, transferido, porcentaje, status, fecha):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO orden_future(id, orderID, symbol, clientOrderId, type, side, precioE, precioCS, cont, transferido, porcentaje, status, fecha ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(consulta, ('null', orderID, symbol, clientOrderId, typeS, side, precioE, precioCS, cont, transferido, porcentaje, status, fecha ))
            con.commit()
            return guardar
            
    finally:
        con.close()

def guardarVolumenTransferido(entrada, costo, restante, comision, id_orden, fecha):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO volumenoperacion(id, entrada, costo, restante, comision,  id_orden, fecha ) VALUES (%s, %s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(consulta, ('null', entrada, costo, restante, comision,  id_orden, fecha ))
            con.commit()
            return guardar
            
    finally:
        con.close()


def guardarTransferencia(tranId, typeS, asset, amount, fecha):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO transferencia(id, tranId, type, asset, amount, fecha) VALUES (%s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(consulta, ('null', tranId, typeS, asset, amount, fecha ))
            con.commit()
            return guardar
            
    finally:
        con.close()

def insertarOrdenCompra(symbol, orderId, cantidadM, cantidadE, typeS, side, precioM, comisionM, fecha):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = 'INSERT INTO orden_compra(id, symbol, orderId, cantidadM, cantidadE, type, side, precioM, comisionM, fecha) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
            guardar = cur.execute(consulta, ('null', symbol, orderId, cantidadM, cantidadE, typeS, side, precioM, comisionM, fecha ))
            con.commit()
            return guardar
            
    finally:
        con.close()


def consultarOrdenesfuture():
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM orden_future where status = 1')
            rows = cur.fetchall()
            return rows
            
    finally:
        con.close()

def updateConsulta(consulta):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            
            guardar = cur.execute(consulta)
            con.commit()
            return guardar
            
    finally:
        con.close()

#consultas binance


def crearOrdenFuture(symbol, side, cantidad):
    try:
        result = client.futures_coin_create_order(symbol=symbol, side=side, type='MARKET', quantity=cantidad )
    except BinanceAPIException as e:
        print(e)
        return 0
    else:
        return result

def ordenCompraBinance(symbol, side, monto):
    try:
        result = client.create_order(symbol=symbol, side=side, type="MARKET", quoteOrderQty=monto)
    except BinanceAPIException as e:
        print(e)
        return 0
    else:
        return result

def ordenVentaBinance(symbol, side, monto):
    try:
        result = client.create_order(symbol=symbol, side=side, type="MARKET", quantity=monto)
    except BinanceAPIException as e:
        print(e)
        return 0
    else:
        return result

def transferenciaBiance(types, asset, amount):
    try:
        result = client.universal_transfer(type=types, asset=asset, amount=amount, newOrderRespType='RESULT')
    except BinanceAPIException as e:
        return e
    else:
        return result

def getDiferencia(id, invertido, cont, moneda, symbol, diferenciaInicial):
    #ponderado spot 
    getBookSpot = get_spot_book(symbol=moneda+'USDT', limit=50)
    ponderadoSpot = getPromedioPonderado(getBookSpot, invertido, 'bids')
    #ponderado future
    getBookFuture = get_future_coin_book(symbol=symbol, limit=50)
    ponderadoFuture = getPromedioPonderadoFuture(getBookFuture, cont, 'asks')
    diferenciaNueva = (( float(ponderadoFuture) / float(ponderadoSpot) ) * 100 )- 100
    sql = f"update orden_future   set precioS =  {ponderadoFuture}, precioSS = {ponderadoSpot}   where id = {id} " 
    actualizar = updateData(sql)
    print('diferencia inicial',diferenciaInicial)
    print('diferencia Nueva',diferenciaNueva)
    return diferenciaNueva

def getVolumenOperacion(order_id):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = "SELECT * FROM volumenoperacion where id_orden = %s;"
            cur.execute(consulta, (order_id))
            rows = cur.fetchone()
            return rows
    finally:
        con.close()

def getOrdenesbySimbol(symbol):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = "SELECT COUNT(*) FROM orden_future where status = 1 and symbol = %s;"
            cur.execute(consulta, (symbol))
            rows = cur.fetchone()
            return rows
    finally:
        con.close()


def getPreciosEntrada(order_id):
    con = pymysql.connect(host=host,   user=userDb,   password=userPass,    db=database)
    try:
        with con.cursor() as cur:
            consulta = "SELECT precioE, precioCS, symbol FROM orden_future where orderID = %s;"
            cur.execute(consulta, (order_id))
            rows = cur.fetchone()
            return rows
            
    finally:
        con.close()


def getAssetPrice(asset):
    try:
        result = client.get_ticker(symbol=asset)
    except BinanceAPIException as e:
        print(e)
        return 0
    else:
        return result



#promedios ponderados 

def get_spot_book(symbol, limit):
    try:
        result = client.get_order_book(symbol=symbol, limit=limit)
    except BinanceAPIException as e:
        print(e)
        return 0
    else:
        return result

def get_future_coin_book(symbol, limit):
    try:
        result = client.futures_coin_order_book(symbol=symbol, limit=limit)
    except BinanceAPIException as e:
        print(e)
        return 0
    else:
        return result


def getPromedioPonderado(listaBook, compra, bidsAsks):
    volumenPrecio = 0; 
    volumenMoneda = 0
    promedioEmpoderado = 0
    for bid in listaBook[bidsAsks]:
        volumenPrecioNuevo = float(bid[0]) * float(bid[1]) + volumenPrecio
        if(volumenPrecioNuevo >= compra):
            precioNuevo =( (compra - volumenPrecio) / float(bid[0]) ) + volumenMoneda
            promedioEmpoderado = compra / precioNuevo
            volumenPrecio = float(bid[0]) * float(bid[1]) + volumenPrecio
            volumenMoneda = float(bid[1]) + volumenMoneda
            break
        else:
            volumenPrecio = float(bid[0]) * float(bid[1]) + volumenPrecio
            volumenMoneda = float(bid[1]) + volumenMoneda
    return promedioEmpoderado


def getPromedioPonderadoFuture(listaBook, compra, bidsAsks):
    volumenPrecio = 0; 
    cont = 10
    precioProducto = 0
    compra = compra /cont
    promedioEmpoderado = 0
    for bid in listaBook[bidsAsks]:
        volumenPrecioNuevo = float(bid[1])  + volumenPrecio
        if(volumenPrecioNuevo >= compra):
            volumenPrecio =  (float(bid[1]) )+ volumenPrecio
            precioProducto = (float(bid[0]) * float(bid[1]) )+ precioProducto
            promedioEmpoderado = precioProducto / volumenPrecio
            break
        else:
            volumenPrecio =  (float(bid[1]) )+ volumenPrecio
            precioProducto = (float(bid[0]) * float(bid[1]) )+ precioProducto
    return promedioEmpoderado

#fin promedios ponderados 
#realizar transacciones 


def manual():
     ordenFutures = consultarOrdenesfuture()
     cantOrdenes = len(ordenFutures)
     if cantOrdenes>0:
        print("si hay ordenes futuras abiertas")
        #ejecutar orden de compra 
        for row in ordenFutures:
            diferenciaInicial = float(row[6]) / float(row[7]) *100 -100
            cerrarEn = float(row[11])
            symbolFuture = row[2]
            moneda = row[2]
            moneda = moneda[0:3]
            if moneda == 'LIN':
                moneda = 'LINK'
            if cerrarEn == 0:
                cerrarEn = 5
            DineroInvertidoExacto = float(row[6])*float(row[9])
            diferenciaNew = getDiferencia(row[0], DineroInvertidoExacto, row[8], moneda, symbolFuture, row[10] )
            updateOrdenFuture = updateConsulta('update orden_future set porcentaje = '+str(diferenciaNew)+' where orderId = '+str(row[1]))
            print("ini: "+str(diferenciaInicial)+"- nueva: "+str(diferenciaNew))
            porcentajeActual = diferenciaInicial - diferenciaNew
            print(porcentajeActual)
            if porcentajeActual >= cerrarEn:
                print("cerrar orden ")
                print("quanty", row[8])
                Fo = crearOrdenFuture(symbolFuture, 'BUY', row[8] )
                print(Fo)
                if Fo != 0:
                    print("se hizo la orden")
                    #cerrar y ya
                    print("se actualizo la orden")
                    #ahora transferir buscar disponible 
                    #buscar si hay varias ordenes del mismo simbolo 
                    getOrden = client.futures_coin_get_order(symbol=symbolFuture, orderId=Fo["orderId"])
                    OrdenesMismoSimbolo = getOrdenesbySimbol(symbolFuture)
                    if OrdenesMismoSimbolo[0]>1:
                        comision = client.futures_coin_income_history(symbol=symbolFuture, incomeType='COMMISSION', limit=1)
                        comision = comision[0]["income"].replace('-','')
                        #nito el markprice de cierre 
                        markPriceCierre = getOrden["avgPrice"]
                        roe = ((float(row[6]) / float(markPriceCierre)) *100) -100
                        volumenOperacion = getVolumenOperacion(row[1])
                        print(volumenOperacion)
                        comisionVieja = volumenOperacion[4]
                        valorContrato = volumenOperacion[2]
                        montoEntrada =  volumenOperacion[1]
                        porcentajeRoe = (float(valorContrato) * float(roe)) / 100
                        montoTransferir = float(montoEntrada) - (float(comision) + float(comisionVieja) )
                        if roe >0:
                            montoTransferir = float(montoTransferir) + float(porcentajeRoe)
                        else:
                            montoTransferir = float(montoTransferir) - float(porcentajeRoe)

                    else:
                        disponible = client.futures_coin_account_balance()
                        n = searchAssetinAccount(disponible, moneda)
                        balanceDisponible = disponible[n]["availableBalance"]
                        montoTransferir = balanceDisponible
                    cierreFuture = getOrden["avgPrice"]
                    
                    #le voy a quitar el 0.2% por probar 
                    updateOrdenFuture = updateConsulta('update orden_future set status = 0 where orderId = '+str(row[1]))
                    print("monto transferir", montoTransferir)
                    Tr = transferenciaBiance('CMFUTURE_MAIN', moneda, montoTransferir)
                    print(Tr)
                    if Tr != 0:
                      #guardar transferencia en base de datos
                      saveTran = guardarTransferencia(Tr["tranId"], 'CMFUTURE_MAIN', moneda, montoTransferir, datetime.now() )
                      #buscar balance en spot 
                      
                      if(moneda == 'DOT'):
                        montoTransferir = math.floor(float(montoTransferir) * 100)/100.0
                      if(moneda == 'LINK'):
                        montoTransferir = math.floor(float(montoTransferir) * 100)/100.0
                      if(moneda == 'ADA'):
                        montoTransferir = math.floor(float(montoTransferir) * 10)/10.0
                      if(moneda == 'ETH'):
                        montoTransferir = math.floor(float(montoTransferir) * 10000)/10000.0
                      if(moneda == 'BNB'):
                        montoTransferir = math.floor(float(montoTransferir) * 1000)/1000.0
                      if(moneda == 'XRP'):
                        montoTransferir = math.floor(float(montoTransferir) * 1)/1.0
                      if(moneda == 'BCH'):
                        montoTransferir = math.floor(float(montoTransferir) * 1000)/1000.0
                      if(moneda == 'LTC'):
                        montoTransferir = math.floor(float(montoTransferir) * 1000)/1000.0
                      if(moneda == 'BTC'):
                        montoTransferir = math.floor(float(montoTransferir) * 100000)/100000.0
                     
                      print("monto a vender :", montoTransferir)
                      Or = ordenVentaBinance(moneda+'USDT', 'SELL', montoTransferir)
                      
                      print(Or)
                      if Or != 0:
                        #guardar precio de compra de la moneda 
                        preCompra = 0
                        con = 0
                        for comi in Or["fills"]:
                            preCompra = float(comi["price"]) + preCompra
                            con = con+1

                        precioCompraSpot = preCompra /con
                        cantidadMonedaComprada= Or["origQty"]
                        comision = Or["fills"][0]["commission"]
                        cantidadTransferir = float(cantidadMonedaComprada)
                        idOrden = row[0]
                        diferenciaFinalCierre = ( float(cierreFuture) / float(precioCompraSpot) ) * 100 - 100
                        sql = f"update orden_future   set porcentaje = {diferenciaFinalCierre}, precioS =  {cierreFuture}, precioSS = {precioCompraSpot} where id = {idOrden} " 
                        actualizar = updateData(sql)
                        CrearOrdenCompra = insertarOrdenCompra(Or["symbol"], Or["orderId"], Or["origQty"], Or["cummulativeQuoteQty"], Or["type"], Or["side"], Or["fills"][0]["price"], Or["fills"][0]["commission"], datetime.now())
               # else:
                   # print("no se hizo la orden")
     #else:
         #print("no hay ordenes ")
        
    


def ejecutarScript():
    try:
        resultado = manual()
    except:
        print("Hay un error en los valores de entrada")
    
while True:
    ejecutarScript()

