import json
import pandas as pd
import numbers

with open("data_structure.json", "r", ) as f:
    data_structure = json.load(f)

def sanity_check(data):
    '''
    Checks variables names, ranges, and types.
    Returns report as string.
    '''
    problems_header = "\n\nSANITY CHECK SUMMARY:\n"
    problems = ""

    problems += check_variables(data)
    problems += check_ranges(data)
    problems += check_types(data)

    if (len(problems) == 0):
        problems += "No problems found during sanitazion check."

    answer = problems_header + problems
    
    return(data, answer)

def check_variables(data):
    '''
    Checks if the variables are the expected ones, returns report as string.
    '''
    given_set = set(data.columns)
    expected_set = set(data_structure.keys())

    # Variables missing in data:
    missing = expected_set.difference(given_set)
    garbage = given_set.difference(expected_set)
    veredict = ""

    if (len(missing) > 0):
        veredict += "The following variables are missing: " + str(missing) + "\n"
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
            if isinstance(value, numbers.Number) and not pd.isna(value):
                if not (var_range[0] <= value <= var_range[1]):
                    veredict += "Variable " + variable + " is out of range.\n"
    return(veredict)

def check_types(data):
    '''
    Checks data types, returns report as string.
    '''
    veredict = ""

    for variable in data_structure.keys():
        var_type = data_structure[variable]["type"]
        value = data[variable][0]
        if (var_type == "Numeric"):
            if not (isinstance(value, numbers.Number)):
                veredict += "El valor de " + variable + " no es numérico.\n"
        if (var_type == "String"):
            if not (isinstance(value, str)):
                veredict += "El valor de " + variable + " no es texto.\n"

    return(veredict)
