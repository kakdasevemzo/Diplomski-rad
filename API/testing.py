import sondehub

def on_message(message):
    print(message)

print(f'Started streaming data...')
test = sondehub.Stream(on_message=on_message)

while 1:
    pass
