from rufous import rufous

@rufous
def add(a, b):
    return a+b

add.delay(1, 4)