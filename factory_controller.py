import asyncio
from time import sleep
import requests

# Storage specs 6x9=54 x2=108 x2=216


PUT_ADDR = 'http://localhost:7410/api/tag/values/by-name'
GET_ADDR = 'http://localhost:7410/api/tag/values/by-name'
TICK_DELAY = 0.02
# Query
in_query = set()
# Semaphores
sklad1_move = False


async def create_new_tag(new_value):
    if not new_value:
        return
    print(f'Create new tag {in_query}')
    base = [
        ('RFID Reader 11 Command', 3),
        ('RFID Reader 11 Memory Index', 1),
        ('RFID Reader 11 Write Data', in_query.pop()),
        ('RFID Reader 11 Execute Command', True)
    ]
    requests.put(PUT_ADDR, json=tuple_to_gavno(base))
    sleep(TICK_DELAY)
    base = [
        ('RFID Reader 11 Execute Command', False)
    ]
    requests.put(PUT_ADDR, json=tuple_to_gavno(base))


async def sklad1(new_value):
    global sklad1_move
    if not new_value or sklad1_move:
        return
    put([('StopR 1 Out', True)])
    base = [
        ('RFID In Command', 2),
        ('RFID In Memory Index', 1),
        ('RFID In Execute Command', True)
    ]
    put(base)
    sleep(TICK_DELAY)
    base = [
        ('RFID In Execute Command', False)
    ]
    put(base)
    sleep(TICK_DELAY)
    ans = get(['RFID In Read Data'])
    if ans[0]['value'] <= 108:
        put([('CT 1 (+)', False),('CT 1 Left', True),('CT 1A Right', True)])
        sklad1_move = True
        spawn_item(2, 2, 109)
    else:
        put([('StopR 1 Out', False)])
        spawn_item(3, 2, 2)


async def sklad1_leave(new_value):
    global sklad1_move
    if not new_value or not sklad1_move:
        return
    put([('CT 1 (+)', True), ('CT 1 Left', False), ('CT 1A Right', False), ('StopR 1 Out', False)])
    sklad1_move = False


CALLBACKS = {
    'RS 1 In': create_new_tag,
    'CS 1': sklad1,
    'RS 1A Out': sklad1_leave,
}


def spawn_item(part, base, address):
    global in_query
    in_query.add(address)
    base = [
        {
            'name': 'Emitter 1 (Part)',
            'value': part
        },
        {
            'name': 'Emitter 1 (Base)',
            'value': base
        },
        {
            'name': 'Emitter 1 (Emit)',
            'value': True
        }
    ]
    requests.put(PUT_ADDR, json=base)
    sleep(0.1)
    stop = [
        {
            'name': 'Emitter 1 (Emit)',
            'value': False
        }
    ]
    requests.put(PUT_ADDR, json=stop)


def tuple_to_gavno(tuple_list):
    return [{'name':i[0],'value':i[1]} for i in tuple_list]


def run_rollers():
    base = [
        ('RC (4m) 1.1', True),
        ('CT 1 (+)', True),
        ('RC A1', True),
        ('Curved RC A2', True),
        ('RC A3', True),
        ('Load RC A4', True),
        ('RC (6m) 1.2', True),
    ]
    requests.put(PUT_ADDR, json=tuple_to_gavno(base))


ans_old = False
ans = {}


def main_cycle():
    global ans_old, ans
    base = [
        "RS 1 In",
        "RFID In Read Data",
        "CS 1",
        "CS 1A",
        "RS 1A Out",
        "RFID A1 Read Data",
        "At Load A",
        "At Middle A"
    ]
    ans = requests.get(GET_ADDR, json=base)
    ans = ans.json()
    ans = {i['name']:i['value'] for i in ans}
    callbacks = []
    if ans_old:
        for i in ans:
            if ans[i] != ans_old[i] and i in CALLBACKS:
                callbacks.append((i, ans[i]))
    for i in callbacks:
        asyncio.run(CALLBACKS[i[0]](i[1]))
    ans_old = ans
    sleep(TICK_DELAY)


def put(base):
    return requests.put(PUT_ADDR, json=tuple_to_gavno(base)).json()


def get(base):
    return requests.get(GET_ADDR, json=base).json()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    spawn_item(1,2,1)
    run_rollers()
    while True:
        main_cycle()
