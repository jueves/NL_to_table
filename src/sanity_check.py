import json
import pandas as pd
from pandas.api.types import is_bool_dtype, is_number
import datetime

with open("data_structure.json", "r", encoding="utf-8") as f:
    data_structure = json.load(f)

def sanity_check(data):
    '''
    Checks variables names, ranges, and types.
    Returns report as string.
    '''
    problems = check_variables(data)
    problems += check_ranges(data)
    problems += check_types(data)
    if len(problems) > 0:
        problems = "\n\nSANITY CHECK SUMMARY:\n" + problems
    return(problems)

def check_variables(data):
    '''
    Checks if the variables are the expected ones, returns report as string.
    '''
    given_set = set(data.columns)
    expected_set = set(data_structure.keys())

    # Check for unsolicited variables in data:
    garbage = given_set.difference(expected_set)
    veredict = ""

    if (len(garbage) > 0):
        veredict += "The following variables where not asked for: " + str(garbage) + "\n"

    return(veredict)

def check_ranges(data):
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
                    veredict += "Variable " + variable + " is out of range.\n"
    return(veredict)

def check_types(data):
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