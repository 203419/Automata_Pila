from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import re

app = Flask(__name__)
CORS(app)


exp_all = {
    "exp_var": {
        "Tipo": r"X|Y|A|B",
        "Nombre": r"[a-z][a-z0-9]*",
        "Asignacion": r"=",
        "Numero": r"[0-9]+",
        "String": r'"[^"]*"',
        "Double": r"[0-9]+\.[0-9]+",
        "Boolean": r"true|false",
    },
    "exp_func": {
        "PalabraR": r"LT",
        "Nombre": r"[a-z][a-z0-9]*",
        "Llaves": r"<>",
        "DosPuntos": r":",
        "Contenido": r".+$",
    },
    "exp_cic": {
        "PalabraR": r"RT",
        "Sentencia1": r"[a-z][a-z0-9]*",
        "Operador": r"==|!=|<|>|<=|>=",
        "Sentencia2": r"[0-9]+|true|false",
        "DosPuntos": r":",
        "Contenido": r".+$",
    },
    "exp_main": {
        "PalabraR": r"Start",
        "DosPuntos": r":",
        "Contenido": r".+$",
    },
}


def obtener_claves_v(pila):
    return [clave for valor in pila if (clave := next((k for k, v in exp_all["exp_var"].items() if v == valor), None)) is not None]

def automata_pila_variable(cadena):
    exp_v = exp_all["exp_var"]

    pila = ["$", exp_v["Asignacion"], exp_v["Nombre"]]
    registros_pila = []

    tipo = re.match(exp_v["Tipo"], cadena)
    if tipo and tipo.group() == 'X':
        pila.append(exp_v["Tipo"])
        pila.insert(1, exp_v["Numero"])
    elif tipo and tipo.group() == 'Y':
        pila.append(exp_v["Tipo"])
        pila.insert(1, exp_v["String"])
    elif tipo and tipo.group() == 'A':
        pila.append(exp_v["Tipo"])
        pila.insert(1, exp_v["Double"])
    elif tipo and tipo.group() == 'B':
        pila.append(exp_v["Tipo"])
        pila.insert(1, exp_v["Boolean"])
    
    cadena = cadena + " $" 
    elementos = cadena.split()

    init = 0 
    while pila[-1] != "$":
        registros_pila.append(obtener_claves_v(pila))
        X = pila[-1] 
        a = elementos[init]

        if re.match(X, a):
            pila.pop()
            init += 1
        else:
            return False, registros_pila

    registros_pila.append(obtener_claves_v(pila))
    return True, registros_pila


def obtener_claves_func(pila):
    return [clave for valor in pila if (clave := next((k for k, v in exp_all["exp_func"].items() if v == valor), None)) is not None]

def automata_pila_func(cadena):
    pila = ["$"] + list(exp_all["exp_func"].values())[::-1]
    registros_pila = []

    cadena = cadena + " $"
    elementos = cadena.split()
    init = 0

    while pila[-1] != "$":
        registros_pila.append(obtener_claves_func(pila))
        X = pila[-1]
        a = elementos[init]

        if re.match(X, a):
            pila.pop()
            init += 1
        else:
            return False, registros_pila
        
    registros_pila.append(obtener_claves_func(pila))
    return True, registros_pila


def obtener_claves_cic(pila):
    return [clave for valor in pila if (clave := next((k for k, v in exp_all["exp_cic"].items() if v == valor), None)) is not None]

def automata_pila_cic(cadena):
    pila = ["$"] + list(exp_all["exp_cic"].values())[::-1]
    registros_pila = []

    cadena = cadena + " $"
    elementos = cadena.split()
    init = 0

    while pila[-1] != "$":
        registros_pila.append(obtener_claves_cic(pila))
        X = pila[-1]
        a = elementos[init]

        if re.match(X, a):
            pila.pop()
            init += 1
        else:
            return False, registros_pila
        
    registros_pila.append(obtener_claves_cic(pila))
    return True, registros_pila

def obtener_claves_cond(pila):
    return [clave for valor in pila if (clave := next((k for k, v in exp_all["exp_cic"].items() if v == valor), None)) is not None]

def automata_pila_cond(cadena):
    pila = ["$"] + list(exp_all["exp_cic"].values())[::-1]
    print(pila)
    registros_pila = []

    cadena = cadena + " $"
    elementos = cadena.split()
    init = 0

    while pila[-1] != "$":
        registros_pila.append(obtener_claves_cond(pila))
        if pila[-1] == "RT":
            pila.pop()
            pila.append("RB")
        
        X = pila[-1]
        a = elementos[init]

        if re.match(X, a):
            pila.pop()
            init += 1
        else:
            return False, registros_pila
        
    registros_pila.append(obtener_claves_cond(pila))
    return True, registros_pila

def obtener_claves_main(pila):
    return [clave for valor in pila if (clave := next((k for k, v in exp_all["exp_main"].items() if v == valor), None)) is not None]

def automata_pila_main(cadena):
    pila = ["$"] + list(exp_all["exp_main"].values())[::-1]
    registros_pila = []

    cadena = cadena + " $"
    elementos = cadena.split()
    init = 0

    while pila[-1] != "$":
        registros_pila.append(obtener_claves_main(pila))
        X = pila[-1]
        a = elementos[init]

        if re.match(X, a):
            pila.pop()
            init += 1
        else:
            return False, registros_pila
        
    registros_pila.append(obtener_claves_main(pila))
    return True, registros_pila

def evaluar_cadena_automatico(cadena):
    prefijo = cadena.split()[0]

    if prefijo == "LT":
        tipo_estructura = "Función"
        resultado, registros_pila = automata_pila_func(cadena)
    elif prefijo == "RT":
        tipo_estructura = "Ciclo"
        resultado, registros_pila = automata_pila_cic(cadena)
    elif prefijo == "RB":
        tipo_estructura = "Condicional"
        resultado, registros_pila = automata_pila_cond(cadena)
    elif prefijo == "Start":
        tipo_estructura = "Main"
        resultado, registros_pila = automata_pila_main(cadena)
    elif prefijo in ["X", "Y", "A", "B"]:
        tipo_estructura = "Variable"
        resultado, registros_pila = automata_pila_variable(cadena)
    else:
        print("Cadena no reconocida")
        return False, []

    return resultado, registros_pila, tipo_estructura


@cross_origin()
@app.route('/verificar_automatico', methods=['POST'])
def verificar_automatico():
    data = request.get_json()
    cadena = data.get('cadena', '')
    resultado, registros_pila, tipo_estructura = evaluar_cadena_automatico(cadena)
    return jsonify({"resultado": resultado, "pasos": registros_pila, "tipo_estructura": tipo_estructura})

if __name__ == '__main__':
    app.run(debug=True)
    