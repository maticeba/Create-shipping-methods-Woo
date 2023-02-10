from woocommerce import API
import json
import gspread

gc = gspread.service_account('nacho-375314-f64d7f6a3439.json')
sheetChile = 'States de Chile (Woo)'
# https://docs.google.com/spreadsheets/d/1foS7YqU5-HpnGddlXw4p-YW4Iq6z6u92UiECEUskPFQ/edit?usp=sharing
sheetMexico = 'States de Mexico (Woo)'
# https://docs.google.com/spreadsheets/d/1EuwgJRuPlfm6wm37L8VrDG4PXb1wbAILfl4aRFpWiLY/edit?usp=sharing
sheetArgentina = 'States de Argentina (Woo)'
# https://docs.google.com/spreadsheets/d/19tzWo4JbzQV0i6RhNusfbFXjg2Y1QKx4y_XFXQgBLK8/edit?usp=sharing
sh = None

wcapi = API(
    url="https://woo-test.clicoh.com/",
    consumer_key="inserteSuKeyAqui",
    consumer_secret="inserteSuSecretAqui",
    version="wc/v3",
    timeout=10)

method_data = {
    "method_id": "apg_shipping",
    "settings": {
        "title": "Envio a domicilio ClicOH",
        "tarifas": "",
        "muestra_icono": "no"
    }
}


def crear_shipping_methods():
    cantidadRegiones = len(sh.worksheet("Regiones").row_values(1))
    tarifas = crearTarifas()
    for i in range(cantidadRegiones):
        if len(tarifas) != 0:
            method_data["settings"]["tarifas"] = tarifas[i]
        crear_zona(sh.worksheet("Regiones").col_values(i+1))
    print('\nFin de ejecución\n')


def crearTarifas():
    cadena = ""
    tarifas = []
    cantidadRegiones = len(sh.sheet1.row_values(1))
    for i in range(1, cantidadRegiones*2, 2):
        pesos = sh.worksheet("TarifasPorPeso").col_values(i)
        pesos.pop(0)
        precios = sh.worksheet("TarifasPorPeso").col_values(i+1)
        precios.pop(0)
        for j in range(len(pesos)):
            cadena = cadena + pesos[j] + '|' + precios[j] + '\n'
        tarifas.append(cadena)
        cadena = ""
    return tarifas


def validarDecision(pais: str):
    decision = input(
        f'\n¿Esta seguro de cargarle los métodos de envío de {pais} al seller {wcapi.url}? \nResponda SI/NO: ')
    return not (decision == 'SI' or decision == "si" or decision == "Si")


def crear_zona(columna: list):
    nombreZona = columna[0]
    data = {"name": nombreZona}

    # Crear la zona
    id_zona = (wcapi.post("shipping/zones", data).json())['id']

    # Agregar los cps/states a la zona creada
    try:
        wcapi.put(
            f"shipping/zones/{id_zona}/locations", buscarValue(columna)).json()
    except:
        print(
            f"\nHa ocurrido un error al cargar {nombreZona} \n")
    else:
        print(f"\n{nombreZona} actualizada con éxito! \n")

    # Crear el método de envío: Envío a domicilio ClicOH
    wcapi.post(f"shipping/zones/{id_zona}/methods", method_data)


def buscarValue(columna: list):
    # Quitamos la region (primer elemento de la lista)
    columna.pop(0)
    returned_json = '['
    for value in columna:
        returned_json = returned_json + agregarValueAJson(value) + ','
    # Eliminamos la ultima coma y cerramos lista
    returned_json = returned_json[:-1] + ']'
    return json.loads(returned_json)


def agregarValueAJson(value: str):
    try:
        int(value)
        return '{"code": "' + value + '", "type": "postcode"}'
    except:
        return '{"code": "' + value + '", "type": "state"}'


def mostrarBienvenida():
    return print(f"""\n***Creador de Regiones y Métodos de envío WOO***
    \n 1) CL \n 2) MX \n 3) ARG\nSeller a modificar: {wcapi.url}""")


def validarPais(pais: str):
    global sh
    match pais:
        case 'CL':
            sh = gc.open(sheetChile)
        case 'MX':
            sh = gc.open(sheetMexico)
        case 'ARG':
            sh = gc.open(sheetArgentina)
        case _:
            print('\nDebe ingresar un país válido!!!\n')
            return

    if validarDecision(pais):
        print('\nFin de ejecución\n')
        return

    crear_shipping_methods()


if __name__ == '__main__':
    mostrarBienvenida()
    validarPais(input('Escriba las siglas del país a cargar: '))
