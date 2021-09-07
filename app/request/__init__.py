from flask import render_template,  request, jsonify,  redirect, url_for, session
from app import app
#modulo de binance , aqui esta la conexion y las funciones q cree para operar con binance
from app.modulos.binance import client, calcularDias, crearOrdenCompraBinance, cerrarOrdenBinance 
#fin modulo binance
from app.schemas import * #aqui esta la conexion con la base de datos y sus funciones
# y ademas importa de una vez los datos del archivo datos.py
from datetime import datetime

usernameDb = datos["usernameDb"]
passDb = datos["passDb"]

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

@app.route("/okex")
def okex():
    if 'loggedin' in session:
        datosTabla = getData(
            'SELECT * FROM tabla_futures order by dir_rate desc')
        return render_template("exchangeIndex/okex.html", datos=datosTabla)
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