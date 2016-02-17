from rufous import rufous


@rufous
def add(a, b):
    return a+b

if __name__ == '__main__':
    add.delay(1, 4)
