from ..utilities import utils
from ..utilities import constants


def validateInputTaxonomyData(validationBody, field_properties):
    validationList = []
    for properties in field_properties:
        validationList.append({
           "key" : properties.get('field_name',None),
           "value": validationBody.get(properties.get('field_name'), None),
           "validations" : properties.get('validations',None)
        })

    errors = validate(validationList)

    if len(errors):
        raise utils.MyException(errors)
    

def validate(validationOptionsList):
    validation_errors = []

    for item in validationOptionsList:
        if item['validations'].get(constants.MAX_VALUE, 0):
            if not utils.validateMaxValue(item['value'], item['validations'][constants.MAX_VALUE]):
                validation_errors.append(f"{item['key']} should be less than {item['validations'][constants.MAX_VALUE]}")

        if item['validations'].get(constants.MIN_VALUE, 0):
            if not utils.validateMinValue(item['value'], item['validations'][constants.MIN_VALUE]):
                validation_errors.append(f"{item['key']} should be greater than {item['validations'][constants.MIN_VALUE]}")

        if item['validations'].get(constants.MIN_STRING_LENGTH, 0):
            if not utils.validateMinStringLength(item['value'], item['validations'][constants.MIN_STRING_LENGTH]):
                validation_errors.append(f"{item['key']} string length should be greater than {item['validations'][constants.MIN_STRING_LENGTH]}")
            
        if item['validations'].get(constants.MAX_STRING_LENGTH, 0):
            if not utils.validateMaxStringLength(item['value'], item['validations'][constants.MAX_STRING_LENGTH]):
                validation_errors.append(f"{item['key']} string length should be lesser than {item['validations'][constants.MAX_STRING_LENGTH]}")
            
    return validation_errors