from binance.client import Client
from binance.exceptions import BinanceAPIException
from datos import *
from app.schemas import *
from datetime import datetime, date
import math

# api binance , datos para la api binance
api_key = datos["api_key"]
api_secret = datos["api_secret"]
# finapibinance
# init binance api
client = Client(api_key, api_secret)

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
    # esta compra me trae todos los datos de la misma
    if Or["error"] == 0:
        # continuo no hay errores
        Or = Or["result"]
        print("resultado compra spot binance", Or)

        cantidadMonedaComprada = Or["origQty"]
        preCompra = 0
        comision = 0
        con = 0
        for comi in Or["fills"]:
            # binance cuando es un monto grande hace varias compras entonces realiza varias comisiones y tambien las hace en distintos precios
            comision = float(comi["commission"]) + comision
            preCompra = float(comi["price"]) + preCompra
            con = con+1

        precioCompraSpot = preCompra / con
        cantidadTransferir = float(cantidadMonedaComprada) - float(comision)
        print("precio compra spot", precioCompraSpot)
        print("comision ", comision)
        print("cantidad transferir - comision", cantidadTransferir)
        cantidadenUSDT = Or["cummulativeQuoteQty"]
        print("cantidad en usdt ", cantidadenUSDT)
        # guardo en la db
        CrearOrdenCompra = insertarOrdenCompra(Or["symbol"], Or["orderId"], Or["origQty"], Or["cummulativeQuoteQty"],
                                               Or["type"], Or["side"], Or["fills"][0]["price"], Or["fills"][0]["commission"], datetime.now())
        if CrearOrdenCompra > 0:
            # realizar la transferencia en binance
            Tr = transferenciaBiance(
                'MAIN_CMFUTURE', moneda, cantidadTransferir)
            print("transferencia realizda ", Tr)
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
                    print("monto en monedas", montoEnMonedas)
                    Fo = crearOrdenFuture(symbolFuture, 'SELL', montoEnMonedas)
                    print("orden future ", Fo)
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
                    float(montoTransferir) * 100)/100.0
            if(moneda == 'LINK'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 100)/100.0
            if(moneda == 'ADA'):
                montoTransferir = math.floor(float(montoTransferir) * 10)/10.0
            if(moneda == 'ETH'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 10000)/10000.0
            if(moneda == 'BNB'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 1000)/1000.0
            if(moneda == 'XRP'):
                montoTransferir = math.floor(float(montoTransferir) * 1)/1.0
            if(moneda == 'BCH'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 1000)/1000.0
            if(moneda == 'LTC'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 1000)/1000.0
            if(moneda == 'BTC'):
                montoTransferir = math.floor(
                    float(montoTransferir) * 100000)/100000.0
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
