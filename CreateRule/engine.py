##################################################### engine.py ############################################################


# typical input that we expect to be there

# must be a dict

# import libraries
import pandas as pd
from pyparsing import *
import json

# define global variable output for user to manipulate
output = dict()
# load or define the input df
df = pd.DataFrame()
###################### define function that you wanna define as a part of engine or import them ###########


#################### get the type of data values present in dataframe column
def typeof(column_name):
    return df[column_name].dtype


################## helper function for our model
#### this function takes in a dictionary of items(values) and checks if the item is present in the dictionary or not
def item_in_dict(item,  dict={}, key=False):
    for (ke, val) in dict.items():
        if key == False:
            if val == item:
                return True
        else:
            if ke == item:
                return True
    else:
        return False


#### this returns a key for any value present in dictionary
def key_for_value(val, dict={}):
    li = [key for (key, value) in dict.items() if value == val]
    return li


#### get the column name for particular attribute
def column_name(val, dict={}):
    li = [key for (key, value) in dict.items() if value == val]
    return li


# Temporal_dimension.columns = column_name('temporal_dimension')
# Metric.columns = column_name('metric')
# Categorical_dimension.columns = column_name('categorical_dimension')

def validate(Input):
    assign = Combine('output' + '[\'' + Word(alphanums + '_') + '\']' + ' = ' + ZeroOrMore('column@') + Word(
        alphanums + ' .  [ ] ( ) _ \'  '))
    assignment = ZeroOrMore(assign)
    # defining grammer for if_else condition
    # this can evaluate max two condition at a time
    sign = Word(' < ') | Word(' > ') | Word(' == ') | Word(' -> ')
    condition1 = Combine((Word(alphanums + '. , [ ] ( ) _ \' ') + ZeroOrMore(
        sign + Word(alphanums + '. , [ ] ( ) _ \' ')))).setResultsName('Condition')
    condition2 = Combine(condition1 + 'and' + condition1).setResultsName('and_condition')
    if_condition = 'if' + (condition2 | condition1) + 'then' + '{' + assignment.setResultsName('if_assign') + '}'
    else_condition = ('else' + Word('{') + assignment.setResultsName('else_assign') + '}').setResultsName(
        'else_condition')
    condition = assignment.setResultsName('initial_assign') + ZeroOrMore(if_condition) + ZeroOrMore(else_condition)

    ################################################ evaluation of input ############################
    express = condition.parseString(Input)
    return express


#### function to evaluate the input and provide an output to tkinter
def evaluate(Input, inp=dict()):
    columns = inp.values()
    ################################################### output dictionary #########################
    output = dict()
    ################################################### grammer ###################################
    # defining rules for assignment of output dictionary
    # no space should be there between variable and equals
    ################################################ evaluation of input ############################
    expression = validate(Input)
    #     print(expression)
    if expression.initial_assign:
        print(expression.initial_assign)
        for item in expression.initial_assign:
            if '@' in item:
                exec(item.replace('column@', 'column_name("') + str('", inp)'))
            else:
                exec(item)
    if expression.and_condition:
        print(expression.and_condition[0].replace('&', 'and'))
        print('and_condition evaluated to ', eval(expression.and_condition[0].replace('&', 'and')))
        if eval(expression.and_condition[0].replace('&', 'and')):
            if expression.if_assign:
                #                 print(expression.if_assign)
                for item in expression.if_assign:
                    if '@' in item:
                        exec(item.replace('column@', 'column_name("') + str('", inp)'))
                    else:
                        exec(item)

        elif expression.else_condition:
            #             print('else evaluated to ')
            if expression.else_assign:
                #                 print(expression.else_assign)
                for item in expression.else_assign:
                    if '@' in item:
                        exec(item.replace('column@', 'column_name("') + str('", inp)'))
                    else:
                        exec(item)
    elif expression.Condition:
        print('condition evaluated to ', eval(expression.Condition))
        if eval(expression.Condition.replace('->', 'in')):
            if expression.if_assign:
                #                 print(expression.if_assign)
                for item in expression.if_assign:
                    if '@' in item:
                        exec(item.replace('column@', 'column_name("') + str('", inp)'))
                    else:
                        exec(item)
        elif expression.else_condition:
            if expression.else_assign:
                for item in expression.else_assign:
                    print(item)
                    if '@' in item:
                        exec(item.replace('column@', 'column_name("') + str('", inp)'))
                    else:
                        exec(item)
    return output


#### code to execute all existing rule
# def execute_all():
#     try:
#         temp = pd.read_json('rules.json')
#         for i in range(temp.shape[0]):
#             if temp.status[i] == 'success':
#                 print(evaluate(temp.input[i]))
#         return 'executed successfully'
#     except:
#         return "No Rules To Execute"


def save_code(code):
    rule_dict = {}
    rule_dict['rule'] = [1]
    rule_dict['code'] = [code]
    ind = 0
    try:
        history = pd.read_json('rules.json')
        for item in history.code:
            if item == code:
                return 'Already exist'

        ind = history.index[-1] + 1
        rule_dict['rule'] = ind + 1
        history = history.append(pd.DataFrame(rule_dict, index=[ind]))
        with open('rules.json', 'w') as json_file:
            json.dump(history.to_dict(), json_file)
        return 'Rule saved'
    except:
        history = pd.DataFrame(rule_dict, index=[ind])
        with open('rules.json', 'w') as json_file:
            json.dump(history.to_dict(), json_file)
        return 'Rule saved on a fresh file'


def show():
    df = pd.read_json('rules.json')
    return df.to_dict()


def clean(df):
    date_format = ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y-%d-%m', '%Y%m%d']
    for col in df.columns:
        if df[col].dtype == 'object':
            for i in date_format:
                try:
                    df[col] = pd.to_datetime(df[col], format=i)
                    print('detected date column format as ', i)
                except ValueError:
                    pass

    return df

def get_attributes(df):
    temp = {}
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            temp[col] = 'temporal_dimension'
        elif df[col].dtype == 'float64' or df[col].dtype == 'int64':
            temp[col] = 'metrics'
        else:
            temp[col] = 'categorical'

    return temp


# function to delete the current row
def delete_row(row):
    df = pd.read_json('rules.json')
    try:
        df = df.drop(int(row), axis=0).reset_index().drop('index', axis=1)
        with open('rules.json', 'w') as json_file:
            json.dump(df.to_dict(), json_file)
        out = 'Successfully deleted code with id ' + str(row)
        return out
    except:
        return 'Unable to delete'

# code to execute all existing functions
def execute_all(d = dict()):
    history = pd.read_json('rules.json')
    output = []
    for item in history.code:
        try:
            output.append(evaluate(item, d))
        except:
            output.append('')
    return output

