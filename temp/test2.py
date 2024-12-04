my = None

def myFunc():
    global my
    a = [1,2,3]
    my = a 
myFunc()
print(my)


