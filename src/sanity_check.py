import json
import pandas as pd
from pandas.api.types import is_bool_dtype, is_number
import datetime

def sanity_check(data, data_structure, header=True):
    '''
    Gets a Pandas Data Frame.
    Checks variables names, ranges, and types.
    Returns report as string.
    '''
    valid, problems = check_nlines(data)
    if valid:
        problems += check_variables(data, data_structure)
        problems += check_ranges(data, data_structure)
        problems += check_types(data, data_structure)
    if header and len(problems) > 0:
        problems = "\n\nSANITY CHECK SUMMARY:\n" + problems
    return(problems)

def check_nlines(data):
    '''
    Check the number of lines in data.
    Returns validity (wether exists any data to evaluate) and veredict.
    '''
    valid = True
    veredict = ""
    if len(data) == 0:
        valid = False
        veredict = ("La tabla tiene 0 filas. Se ha solicitado una tabla con 1 fila.")
    elif len(data) > 1:
        veredict = f"Sólo se ha solicitado una fila, se ha devuelto una tabla con {len(data)} filas."
    return(valid, veredict)

def check_variables(data, data_structure):
    '''
    Checks if the variables are the expected ones, returns report as string.
    '''
    given_set = set(data.columns)
    expected_set = set(data_structure.keys())

    # Check for unsolicited variables in data:
    garbage = given_set.difference(expected_set)
    veredict = ""

    if (len(garbage) > 0):
        veredict += "Las siguientes variables no fueron solicitadas: " + str(garbage) + "\n"

    return(veredict)

def check_ranges(data, data_structure):
    '''
    Checks if the values are in range.
    Returns report as string.
    '''
    veredict = ""
    for variable in data_structure.keys():
        var_range = data_structure[variable]["range"]
        if variable in data.columns:
            value = data[variable][0]
            if is_number(value) and not pd.isna(value):
                if not (var_range[0] <= value <= var_range[1]):
                    veredict += "La variable " + variable + " está fuera de rango.\n"
    return(veredict)

def check_types(data, data_structure):
    '''
    Checks data types, returns report as string.
    '''
    veredict = ""

    for variable in data_structure.keys():
        if variable in data.columns:
            var_type = data_structure[variable]["type"]
            value = data[variable][0]
            if not pd.isna(value):
                if (var_type == "Numeric"):
                    if not is_number(value):
                        veredict += "El valor de " + variable + " no es numérico.\n"
                if (var_type == "String"):
                    if not (isinstance(value, str)):
                        veredict += "El valor de " + variable + " no es texto.\n"
                if (var_type == "Time"):
                    if not (isinstance(value, datetime.datetime)):
                        veredict += "El valor de " + variable + " no es un objeto de tiempo.\n"
                if (var_type == "Boolean"):
                    if not is_bool_dtype(value):
                        veredict += "El valor de " + variable + " no es booleano.\n"
    return(veredict)

def validate_data_structure(data_structure_filename):
    '''
    Gets the file name of a json file with a data structure.
    Checks the structure and returns error report as str.
    If no errors found, 'no errors' string will be returned.
    '''
    answer = ""
    try:
        with open(data_structure_filename, "r") as f:
           data_structure = json.load(f)
    except Exception as e:
        answer += f"Error al importar el archivo:\n{e}"

    for var_name in data_structure.keys():
        var = data_structure[var_name]
        try:
            if not isinstance(var["description"], str):
                answer += "\nLa descripción debe de ser un texto entre comillas."
            if not var["type"] in ["String", "Numeric", "Boolean", "Time"]:
                answer += (f"\nError en la variable {var_name}. El apartado 'type' debe ser: "
                            "'String', 'Numeric', 'Boolean' o 'Time'")
            if not isinstance(var["range"], list) or len(var["range"]) not in [0, 2]:
                answer += (f"\nError en la variable {var_name}. El apartado 'range' debe de "
                             "ser una lista de 2 o 0 elementos. Ejemplo: [0, 10] o []")
            if not isinstance(var["example"], list) or not len(var["example"]) == 4:
                answer += (f"\nError en la variable {var_name}. El apartado 'example' debe de "
                             "ser una lista de 4 elementos. Ejemplo: [1, 2, 1, 0]")
            if not isinstance(var["max_empty_days"], int):
                answer += (f"\nError en la variable {var_name}. El apartado 'max_empty_days' debe de "
                             "ser un número. Ejemplo: 30")
            if not var["mute"] in ["True", "False"]:
                answer += (f"\nError en la variable {var_name}. El valor de 'mute' ha de ser"
                             "o bien 'True' o bien 'False'")
        except Exception as e:
            answer += f"\n\nError de formato en la variable {var_name}:\n{e}"
    if len(answer) > 0:
        answer = "Ha habido errores al procesar tu archivo de configuración.\n\n" + answer
    else:
        answer = "no errors"
    return(answer)
