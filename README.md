# Python data validation library
## (Under development)


## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
    - [Basic Usage](#basic-usage)
- [Available rules](#available-rules)
  - [required](#required)
  - [required_with](#required_withfoobar)
  - [required_with_all](#required_with_allfoobar)
  - [required_without](#required_withoutfoobar)
  - [required_without_all](#required_without_allfoobar)
  - [required_if](#required_ifanotherfieldvalue)
  - [required_unless](#required_unlessanotherfieldvalue)
  - [present](#present)
  - [size](#sizevalue)
  - [numeric](#numeric)
  - [integer](#integer)
  - [list](#list)
  - [dict](#dict)
  - [between](#betweenminmax)
  - [min](#minvalue)
  - [max](#maxvalue)
  - [gt](#gtother_field)
  - [gte](#gteother_field)
  - [lt](#ltother_field)
  - [lte](#lteother_field)
- [Extending Validator](#extending-validator)
  - [Custom Validation using callback](#custom-validation-using-callback)
  - [Custom Validation using RuleContract](#custom-validation-using-rulecontract)
- [Credits](#credits)  
- [License](#license)  

## Introduction

`piva` is a simple and powerful library for data validation

```python
from pyva.validator import Validator

validation = Validator(
    {
        'name': 'John',
        'age': 25
    },
    {
        'name':'required',
        'age':' required|min:18'
    }
)

if validation.passes():
# do something cool

```

## Installation

```pip install pyva```

## Usage

### Basic Usage

```python

from pyva.validator import Validator

data = {
    'user': {
        'name': 'John',
        'email': 'johndoe@example.com',
        'age': 25
    }
}

rules = {
    'user': 'required|dict',
    'user.name': 'required|min:3|max:16', # must be at least 3 chars and not more than 16 (16 included )
    'user.email': 'required',
    'user.age': 'required|min:18|max:100',
}

v = Validator(data, rules)

if v.passes():
    validated_data = v.validated()
    print(validated_data)

# or check if it fails
if v.fails():
    print(v.failed_rules)



# You can use list of rules

rules = {
        'user.age': ['required', 'min:18', 'max:100'],
}
v = Validator(data, rules)

```

## Available Rules

### required

The field under validation must be present in the input data and not empty. A field is considered "empty" if one of the following conditions are true:

* The value is None.
* The value is an empty string.
* The value is an empty list,dict... or object that implments \_\_len\_\_ method and len(obj) < 1.

### required_with:foo,bar,...

The field under validation must be present and not empty only if any of the other specified fields are present and not empty.

### required_with_all:foo,bar,...

The field under validation must be present and not empty **only if all** of the other specified fields are present and not empty.

### required_without:foo,bar,...

The field under validation must be present and not empty only when any of the other specified fields are empty or not present.

### required_without_all:foo,bar,...

The field under validation must be present and not empty only when **all** of the other specified fields are empty or not present.

### required_if:anotherfield,value,...

The field under validation must be present and not empty if the anotherfield field is equal to any value.

If you would like to construct more complex condition see [custom rules](#extending-validator)

### required_unless:anotherfield,value,...

The field under validation must be present and not empty unless the anotherfield field is equal to any value.

### present

The field under validation must be present in the input data but can be empty.

### size:value

The field under validation must have a size matching the given value. 
* For string data, value corresponds to the number of characters. 
* For numeric data, value corresponds to a given integer value
* For list,dict,tuple..., size corresponds to the len of the obj

### numeric

The field under validation must be instance of `numbers.Number` or numeric string (strings like '5.6' considered as numeric).

### integer

The field under validation must be an integer.

### list

The field under validation must be instance of list.

### dict

The field under validation must be instance of dict.

### between:min,max

The field under validation must have a size between the given min and max.
Strings, numerics, list, dict... are evaluated in the same fashion as the [size](#sizevalue) rule.

### min:value

The field under validation must have a minimum value. 

### max:value 

The field under validation must be less than or equal to a maximum value.


The field under validation must be instance of dict.

### gt:other_field

The field under validation must be greater than the given field. The two fields must be of the same type.

### gte:other_field

The field under validation must be greater than or equal to the given field. The two fields must be of the same type.

### lt:other_field

The field under validation must be less than the given field. The two fields must be of the same type. 

### lte:other_field

The field under validation must be less than or equal to the given field. The two fields must be of the same type. 

## Extending Validator

### Custom Validation using callback:

```python

from pyva.validator import Validator

def is_odd(attribute, value, fail):
    
    if value % 2 != 0:
        fail("{} must be odd ".format(attribute))
        
data = {
    'length': 20
}

rules = {
    'length': ['required', is_odd] 
}

v = Validator(data, rules)

# or check if it fails
if v.fails():
    print(v.failed_rules) # length must be odd

```

What if you want more powerful validation, well then check [Custom Validation using RuleContract](#custom-validation-using-ruleContract)


### Custom Validation using RuleContract

For this you need to import `RuleContract`


```python

from pyva.Rules.ruleContract import RuleContract
from pyva.validator import Validator

# you class must implement passes() method

class IsOdd(RuleContract):
    
    # use this when you want to pass additional data
    def __init__(self, some_data = None):
        self.some_data = some_data
        

    def passes(self, attribute, value):
        
        if value % 2 == 0:
            return True # return True means validation passed
        
        return False    


data = {
    'length': 20
}

rules = {
    'length': ['required', IsOdd()] 
}

v = Validator(data, rules)

if v.passes():
    # do something cool

```

## Credits

- Inspired by Laravel's [validation syntax](https://laravel.com/docs/8.x/validation)

## License

Licensed under the MIT  license.