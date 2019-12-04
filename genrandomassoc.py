import random
import toml
import string
import uuid

#>>> import string
#>>> string.ascii_letters
#'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
#>>> import random
#>>> random.choice(string.ascii_letters)

data = {"associations": {}}

for i in range(0, 10):
    data["associations"][uuid.uuid4().hex] = uuid.uuid4().hex

with open("assoc.toml", "w") as file:
    toml.dump(data, file)