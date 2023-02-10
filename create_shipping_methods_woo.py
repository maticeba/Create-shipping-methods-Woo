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

wcapi = API(
    url="https://woo-test.clicoh.com/",
    consumer_key="inserteSuKeyAqui",
    consumer_secret="inserteSuSecretAqui",
    version="wc/v3",
    timeout=10)

shipping_data = {
    "method_id": "flat_rate",
    "settings": {
        "title": "Envio a domicilio ClicOH"
    }
}


def crear_shipping_methods(sh: any):
    cantidadRegiones = len(sh.sheet1.row_values(1))
    for i in range(cantidadRegiones):
        crear_zona(sh.sheet1.col_values(i+1))
    print('\nFin de ejecución\n')


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

    # Crear el método de envío - Precio Fijo: cambiar luego por el de clicoh
    wcapi.post(f"shipping/zones/{id_zona}/methods", shipping_data).json()


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

    crear_shipping_methods(sh)


if __name__ == '__main__':
    mostrarBienvenida()
    pais = input('Escriba las siglas del país a cargar: ')
    validarPais(pais)
