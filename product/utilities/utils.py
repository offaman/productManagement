def isAnInteger(value):
    return value.isdecimal()

def isFloatValue(value):
    return value % 1 != 0

def isAnList(object):
    return isinstance(object, list)

def isAnDictionary(object):
    return isinstance(object, dict)

def isAnSet(object):
    return isinstance(object, set)

def isAnTuple(object):
    return isinstance(object, tuple)

def isAnArrayOfDictionaty(object):
    if isAnList(object):
        for item in object:
            if not isinstance(item, dict):
                return False
        return True
    
def isDictionaryEmpty(object):
    if len(object):
        return False
    return True

def isListEmpty(object):
    return bool(len(object))

def isAString(object):
    return isinstance(object,str)

def trimWhiteSpaceDictionaryValue(object):
    if isinstance(object,dict):
        for key in object:
            if object[key] and type(object[key])==dict:
                trimWhiteSpaceDictionaryValue(object[key])
            elif isinstance(object[key], str):
                object[key] = object[key].strip()
    return object

def isListOfStrings(object):
    return isAnList(object) and all(isinstance(item, str) for item in object)


def validateMinValue(value, minValue):
    return value >= minValue

def validateMaxValue(value, maxValue):
    return value <= maxValue


def validateMinStringLength(value, minValue):
    return isAString(value) and len(value) >= minValue


def validateMaxStringLength(value, maxValue):
    return isAString(value) and len(value) <= maxValue


class MyException(Exception):
	def __init__(self, error):
		self.error = error