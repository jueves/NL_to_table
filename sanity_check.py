import json
import pandas as pd
import numbers

with open("data_structure.json", "r") as f:
    data_structure = json.load(f)

def sanity_check(data): 
    problems_header = "\n\nSANITY CHECK SUMMARY:\n"
    problems = ""

    problems += check_variables(data)
    problems += check_ranges(data)

    if (len(problems) == 0):
        problems += "No problems found during sanitazion check."

    answer = data.to_markdown()
    answer += problems_header + problems
    
    return(answer)

def check_variables(data):
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
    veredict = ""
    for variable in data_structure.keys():
        var_range = data_structure[variable]["range"]
        if variable in data.columns:
            value = data[variable][0]
            if isinstance(value, numbers.Number) and not pd.isna(value):
                if not (var_range[0] <= value <= var_range[1]):
                    veredict += "Variable " + variable + " is out of range.\n"
    return(veredict)

'''
# Testing
data = pd.DataFrame(data={'alergy': [11, 2], 'asthma': [13, 4]})

print(check_ranges(data))
'''