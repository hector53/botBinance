from flask import Flask, render_template,  request, jsonify,  redirect, url_for, session
import pymysql
from binance.client import Client
from binance.exceptions import BinanceAPIException
from datetime import datetime, date
import math
import json
import collections

from datos import *
# api binance
api_key = datos["api_key"]
api_secret = datos["api_secret"]
# finapibinance

# datos Host para db
host = datos["host"]
database = datos["database"]
userDb = datos["userDb"]
userPass = datos["userPass"]
# datos Host para db

# init binance api
client = Client(api_key, api_secret)

usernameDb = datos["usernameDb"]
passDb = datos["passDb"]

app = Flask(__name__)
app.secret_key = datos["secret_key_login"]
# mysql q me traigo del otro archivo me da pereza adaptarlas al nuevo


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

# funciones de operaciones
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


def searchAssetinAccount(orden, b):
    rango = range(len(orden))
    index = 0
    for n in rango:
        if orden[n]["asset"] == b:
            index = n
    return index
# fin funciones de operaciones

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

# scripts api binance


def ordenVentaBinance(symbol, side, monto):
    try:
        result = client.create_order(
            symbol=symbol, side=side, type="MARKET", quantity=monto)
    except BinanceAPIException as e:
        return {'error': e.message}
    else:
        return {'error': 0, 'result': result}


def ordenCompraBinance(symbol, side, monto):
    try:
        result = client.create_order(
            symbol=symbol, side=side, type="MARKET", quoteOrderQty=monto)
    except BinanceAPIException as e:
        return {'error': e.message}
    else:
        return {'error': 0, 'result': result}


def transferenciaBiance(types, asset, amount):
    try:
        result = client.universal_transfer(
            type=types, asset=asset, amount=amount, newOrderRespType='RESULT')
    except BinanceAPIException as e:
        return {'error': e.message}
    else:
        return {'error': 0, 'result': result}


def crearOrdenFuture(symbol, side, cantidad):
    try:
        result = client.futures_coin_create_order(
            symbol=symbol, side=side, type='MARKET', quantity=cantidad)
    except BinanceAPIException as e:
        print(e)
        return {'error': e.message}
    else:
        return {'error': 0, 'result': result}

# crear orden


def crearOrdenCompraBinance(symbol, monto):
    MontoUsdt = monto
    symbolFuture = symbol
    moneda = symbol[0:3]
    if moneda == 'LIN':
        moneda = 'LINK'
    Or = ordenCompraBinance(moneda+'USDT', 'BUY', MontoUsdt)
    if Or["error"] == 0:
        # continuo no hay errores
        Or = Or["result"]
        print(Or)

        cantidadMonedaComprada = Or["origQty"]
        preCompra = 0
        comision = 0
        con = 0
        for comi in Or["fills"]:
            comision = float(comi["commission"]) + comision
            preCompra = float(comi["price"]) + preCompra
            con = con+1

        precioCompraSpot = preCompra / con
        cantidadTransferir = float(cantidadMonedaComprada) - float(comision)
        print(cantidadTransferir)
        cantidadenUSDT = Or["cummulativeQuoteQty"]
        print(cantidadenUSDT)
        CrearOrdenCompra = insertarOrdenCompra(Or["symbol"], Or["orderId"], Or["origQty"], Or["cummulativeQuoteQty"],
                                               Or["type"], Or["side"], Or["fills"][0]["price"], Or["fills"][0]["commission"], datetime.now())
        if CrearOrdenCompra > 0:
            # realizar la transferencia en binance
            Tr = transferenciaBiance(
                'MAIN_CMFUTURE', moneda, cantidadTransferir)
            print(Tr)
            if Tr["error"] == 0:
                Tr = Tr["result"]
                # guardar transferencia en base de datos
                saveTran = guardarTransferencia(
                    Tr["tranId"], 'MAIN_CMFUTURE', moneda, cantidadTransferir, datetime.now())
                if saveTran > 0:
                    # crear orden future coin m
                    CostoMoneda = 10
                    if moneda == 'BTC':
                        CostoMoneda = 100

                    # consultar markprice de future para sacar la tasa inicial y sumarselo a los contratos
                    conMarkPrice = client.futures_coin_mark_price(
                        symbol=symbolFuture)
                    tasaInicial = (
                        float(conMarkPrice[0]['markPrice']) / float(precioCompraSpot)) * 100 - 100
                    print("cantidad en USDT", cantidadenUSDT)
                    sacarTasa = (float(cantidadenUSDT) * tasaInicial) / 100
                    sumarTasa = float(cantidadenUSDT) + float(sacarTasa)

                    print("tasa inicial", tasaInicial)
                    print("sacar tasa", sacarTasa)
                    print("sumar tasa", sumarTasa)
                    montoEnMonedas = math.floor(int(sumarTasa) / CostoMoneda)
                    print(montoEnMonedas)
                    Fo = crearOrdenFuture(symbolFuture, 'SELL', montoEnMonedas)
                    print(Fo)
                    if Fo["error"] == 0:
                        Fo = Fo["result"]
                        print("se hizo la orden")
                        # guardar orden en base de datos
                        # buscar precio Entrada
                        getOrden = client.futures_coin_get_order(
                            symbol=symbolFuture, orderId=Fo["orderId"])
                        diferenciaInicialFuture = (
                            (float(getOrden["avgPrice"]) / float(precioCompraSpot)) * 100) - 100
                        saveFuture = guardarFutureOrden(Fo["orderId"], Fo["symbol"], Fo["clientOrderId"], Fo["type"], Fo["side"], getOrden["avgPrice"],
                                                        precioCompraSpot, Fo["origQty"], cantidadTransferir, diferenciaInicialFuture, 1,  datetime.now())
                        comision = client.futures_coin_income_history(
                            symbol=symbolFuture, incomeType='COMMISSION', limit=1)
                        comision = comision[0]["income"].replace('-', '')
                        restante = float(cantidadTransferir) - \
                            float(getOrden["cumBase"])
                        guardarVolumen = guardarVolumenTransferido(str(cantidadTransferir), getOrden["cumBase"], str(
                            restante), comision, Fo["orderId"], datetime.now())
                        return 1
                    else:
                        return Fo["error"]
                else:
                    return {"error": "no se guardo la transferencia"}
            else:
                return Tr["error"]
        else:
            return {"error": "no se guardo la compra"}
    else:
        return Or["error"]


def cerrarOrdenBinance(id):
    # primero buscar la orden por id para saber el numero de contratos y hacer el buy
    datosTabla = getDataOne(f"SELECT * FROM orden_future where orderID = {id}")
    row = datosTabla
    print(row)
    symbolFuture = row[2]
    moneda = symbolFuture[0:3]
    if moneda == 'LIN':
        moneda = 'LINK'
    Fo = crearOrdenFuture(symbolFuture, 'BUY', row[8])
    if Fo["error"] == 0:
        Fo = Fo["result"]
        # buscar ordenes mismo simbolo
        getOrden = client.futures_coin_get_order(
            symbol=symbolFuture, orderId=Fo["orderId"])
        cierreFuture = getOrden["avgPrice"]
        OrdenesMismoSimbolo = getDataOne(
            f"SELECT COUNT(*) FROM orden_future where status = 1 and symbol = '{symbolFuture}'")
        if OrdenesMismoSimbolo[0] > 1:
            print("j")
            comision = client.futures_coin_income_history(
                symbol=symbolFuture, incomeType='COMMISSION', limit=1)
            comision = comision[0]["income"].replace('-', '')
            # nito el markprice de cierre

            markPriceCierre = getOrden["avgPrice"]
            roe = ((float(row[6]) / float(markPriceCierre)) * 100) - 100
            volumenOperacion = getDataOne(
                f"SELECT * FROM volumenoperacion where id_orden = {id}")
            print(volumenOperacion)
            comisionVieja = volumenOperacion[4]
            valorContrato = volumenOperacion[2]
            montoEntrada = volumenOperacion[1]
            porcentajeRoe = (float(valorContrato) * float(roe)) / 100
            montoTransferir = float(montoEntrada) - \
                (float(comision) + float(comisionVieja))
            if roe > 0:
                montoTransferir = float(montoTransferir) + float(porcentajeRoe)
            else:
                montoTransferir = float(montoTransferir) - float(porcentajeRoe)
        else:
            disponible = client.futures_coin_account_balance()
            n = searchAssetinAccount(disponible, moneda)
            balanceDisponible = disponible[n]["availableBalance"]
            montoTransferir = balanceDisponible

        updateOrdenFuture = updateData(
            f"update orden_future set status = 0 where orderId = {id} ")
        print("monto transferir", montoTransferir)
        Tr = transferenciaBiance('CMFUTURE_MAIN', moneda, montoTransferir)
        print(Tr)
        if Tr["error"] == 0:
            Tr = Tr["result"]
            # guardar transferencia en base de datos
            saveTran = guardarTransferencia(
                Tr["tranId"], 'CMFUTURE_MAIN', moneda, montoTransferir, datetime.now())
            # buscar balance en spot

            if(moneda == 'DOT'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 1000)/1000.0
            if(moneda == 'LINK'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 1000)/1000.0
            if(moneda == 'ADA'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 100)/100.0
            if(moneda == 'ETH'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 100000)/100000.0
            if(moneda == 'BNB'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 10000)/10000.0
            if(moneda == 'XRP'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 100)/100.0
            if(moneda == 'BCH'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 100000)/100000.0
            if(moneda == 'LTC'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 100000)/100000.0
            if(moneda == 'BTC'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 1000000)/1000000.0
            Or = ordenVentaBinance(moneda+'USDT', 'SELL', montoTransferir)
            print(Or)
            if Or["error"] == 0:
                # continuo no hay errores
                Or = Or["result"]

                preCompra = 0
                con = 0
                for comi in Or["fills"]:
                    preCompra = float(comi["price"]) + preCompra
                    con = con+1

                precioCompraSpot = preCompra / con
                # guardar precio de compra de la moneda
                diferenciaFinalCierre = (
                    float(cierreFuture) / float(precioCompraSpot)) * 100 - 100
                idOrden = row[0]
                sql = f"update orden_future   set porcentaje = {diferenciaFinalCierre}, precioS =  {cierreFuture}, precioSS = {precioCompraSpot} where id = {idOrden} "
                actualizar = updateData(sql)
                CrearOrdenCompra = insertarOrdenCompra(Or["symbol"], Or["orderId"], Or["origQty"], Or["cummulativeQuoteQty"],
                                                       Or["type"], Or["side"], Or["fills"][0]["price"], Or["fills"][0]["commission"], datetime.now())
                return 1
            else:
                return Or["error"]
        else:
            return Tr["error"]
    else:
        return Fo["error"]

# scripts api binance fin

# request POST


@app.route('/_login_', methods=["POST"])
def loginUser():
    username = request.form.get('user', '', type=str)
    password = request.form.get('pass', '', type=str)
    # ahora hacer el update en la db
    if username == usernameDb and password == passDb:
        result = 1
        session['loggedin'] = True
        session['username'] = username
        print("logueo bien")

    else:
        result = 0

    return jsonify(result=result)


@app.route('/_change_cerrar_en', methods=["POST"])
def changeCerrarEn():
    id = request.form.get('id', 'nada', type=str)
    cierre = request.form.get('cierre', 0, type=str)
    # ahora hacer el update en la db
    sql = f"update orden_future   set cerrarEn =  {cierre}   where id = {id} "
    actualizar = updateData(sql)
    return jsonify(result=actualizar)


@app.route('/_create_orden', methods=["POST"])
def createOrden():
    symbol = request.form.get('id', 'nada', type=str)
    monto = request.form.get('monto', 0, type=str)
    # ahora usar la api de binance y crear la orden :D
    # mejor dicho el sintetico
    crearOrden = crearOrdenCompraBinance(symbol, monto)
    return jsonify(result=crearOrden)


@app.route('/_cerrar_ya', methods=["POST"])
def cerrarOrdenYa():
    id = request.form.get('id', 'nada', type=str)
    # ahora usar la api de binance y cerrar el sintetico :D
    cerrarOrden = cerrarOrdenBinance(id)
    return jsonify(result=cerrarOrden)


@app.route('/_cerrar_manual_', methods=["POST"])
def cerrarManual():
    id = request.form.get('id', 'nada', type=str)
    # ahora usar la api de binance y cerrar el sintetico :D
    sql = f"update orden_future   set status = 2 where id = {id} "
    actualizar = updateData(sql)
    return jsonify(result=actualizar)


@app.route('/_listar_ordenes', methods=["POST"])
def listar_ordenes():
    # ahora usar la api de binance y cerrar el sintetico :D
    datosTabla = getData(
        'SELECT * FROM orden_future where status = 1 order by id desc')
    data = []
    for row in datosTabla:
        tasaInicial = (float(row[6]) / float(row[7])) * 100 - 100
        diferencia = tasaInicial - float(row[10])
        if diferencia > 0:
            diferenciaNueva = "{:.4f}".format(diferencia)
            diferenciaCampo = f"<span class='OrdenDiferenciaP'>{diferenciaNueva}%</span>"
        else:
            diferenciaNueva = "{:.4f}".format(diferencia)
            diferenciaCampo = f"<span class='OrdenDiferenciaN'>{diferenciaNueva}%</span>"

        if int(row[13]) == 1:
            cerrarEnCampo = f"""
                          <div style='display: flex;'> 
                          <input type='number' class='form-control' value='{row[11]}' style='margin-right: 10px;     width: 100px;' id='cerrar_{row[0]}' >
                          <button type='button' class='btn btn-primary' onclick='actualizarCierre({row[0]})'>Ok</button>
                            </div>
                          """
        else:
            cerrarEnCampo = row[11]

        if int(row[13]) == 1:
            statusCampo = f"<span class='OrdenDiferenciaP'>A</span>"
        else:
            statusCampo = f"<span class='OrdenDiferenciaN'>C</span>"

        precioS = row[15]
        precioSS = row[16]
        if precioS != '':
            precioS = "{:.4f}".format(float(precioS))

        if precioSS != '':
            "{:.4f}".format(float(precioSS))

        data.append({
            'symbol': row[2],
            'precioE': "{:.4f}".format(float(row[6])),
            'precioCS': "{:.4f}".format(float(row[7])),
            'precioS': precioS,
            'precioSS': precioSS,
            'tasaIni': "{:.4f}".format(tasaInicial),
            'tasaAct': "{:.4f}".format(float(row[10])),
            'diferencia': diferenciaCampo,
            'cerrarEn': cerrarEnCampo,
            'status': statusCampo,
            'cerrarYa': f"<button type='button' class='btn btn-primary' onclick='cerrarYa({row[1]})'>Cerrar YA</button>",
            'cerrarMa': f"<button type='button' class='btn btn-primary' onclick='cerrarManual({row[0]})'>Cerrar Manual</button>",
            'orderID': row[1],
            'type': row[4],
            'side': row[5],
            'transferido': row[9],
            'cont': row[8],
            'fecha': str(row[14]),

        })

    response = {
        'iTotalRecords': len(data),
        'aaData': data,
    }

    return jsonify(response)


@app.route('/_listar_tabla_futures', methods=["POST"])
def listar_tabla_futures():
    dis = client.futures_coin_mark_price()
   # print(client.response.headers)
    EliminarTablaFuture()
    rango = range(len(dis))
    for n in rango:
        result = dis[n]["symbol"].find('2')
        if result != -1:
            dir_rate = float(dis[n]["markPrice"]) / \
                float(dis[n]["indexPrice"]) * 100 - 100
            diasFaltantes = calcularDias(dis[n]["symbol"])
            annual_rate = dir_rate * 365 / diasFaltantes
            guardarTablaFuture(dis[n]["symbol"], dis[n]["markPrice"], dis[n]["indexPrice"], diasFaltantes,  str(
                dir_rate),  annual_rate,   datetime.now())

    datosTabla = getData('SELECT * FROM tabla_futures order by dir_rate desc')
    return jsonify(datosTabla)


@app.route('/_listar_tabla_orden_', methods=["POST"])
def listar_orden_tabla():
    datosTabla = getData(
        'SELECT * FROM `orden_future` where status = 1 order by id desc')
    return jsonify(datosTabla)

# request POST fin


@app.route("/")
def index():
    if 'loggedin' in session:
        datosTabla = getData(
            'SELECT * FROM tabla_futures order by dir_rate desc')
        return render_template("index.html", datos=datosTabla)
    else:
        return render_template("login.html")


@app.route("/compras")
def compras():
    if 'loggedin' in session:
        datosTabla = getData('SELECT * FROM `orden_compra` order by id desc')
        return render_template("compras.html", datos=datosTabla)
    else:
        return render_template("login.html")


@app.route("/transferencias")
def transferencias():
    if 'loggedin' in session:
        datosTabla = getData('SELECT * FROM `transferencia` order by id Desc')
        return render_template("transferencias.html", datos=datosTabla)
    else:
        return render_template("login.html")


@app.route("/ordenes")
def ordenes():
    if 'loggedin' in session:
        datosTabla = getData(
            'SELECT * FROM `orden_future` where status = 1 order by id desc')
        return render_template("ordenes.html", datos=datosTabla)
    else:
        return render_template("login.html")


@app.route("/ordenesC")
def ordenesC():
    if 'loggedin' in session:
        datosTabla = getData(
            'SELECT * FROM `orden_future` where status != 1 order by id desc')
        return render_template("ordenesC.html", datos=datosTabla)
    else:
        return render_template("login.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route('/salir')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
