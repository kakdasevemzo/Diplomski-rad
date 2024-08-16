import sondehub

def on_message(message):
    print(message)

test = sondehub.Stream(on_message=on_message)
while 1:
    pass