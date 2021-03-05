from pyva.validator import Validator

data = {
    'users': [
        {
            'name': 'John',
            'age': 28
        },
        {
            'name': 'David',
            'age': 19
        }
    ]
}

rules = {
    'users': 'required|list',
    'users.*': 'dict',
    'users.*.name': 'required|min:3',
    'users.*.age': 'required|min:18|max:100',
}

validation = Validator(data, rules)
if validation.passes():
    print(validation.validated())  # get validated data
    # do something cool
