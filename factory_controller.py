import asyncio
import math
from time import sleep
import requests

# Storage specs 6x9=54 x2=108 x2=216


PUT_ADDR = 'http://localhost:7410/api/tag/values/by-name'
GET_ADDR = 'http://localhost:7410/api/tag/values/by-name'
TICK_DELAY = 0.02
PLAN = [2,3,4,5,109,110,111]
# Query
in_query = set()
a_query = list()
b_query = list()
# Semaphores
sklad1_move = False
a_lock = False
b_lock = False

# Callbacks
async def create_new_tag(new_value):
    if not new_value:
        return
    base = [
        ('RFID Reader 11 Command', 1),
        ('RFID Reader 11 Execute Command', True)
    ]
    put(base)
    await asyncio.sleep(TICK_DELAY)
    base = [
        ('RFID Reader 11 Execute Command', False)
    ]
    put(base)
    await asyncio.sleep(TICK_DELAY)
    ans = get(['RFID Reader 11 Read Data'])[0]['value']
    print(f'Tag Serial: {ans}')
    print(f'Create new tag {in_query}')
    base = [
        ('RFID Reader 11 Command', 3),
        ('RFID Reader 11 Memory Index', 1),
        ('RFID Reader 11 Write Data', in_query.pop()),
        ('RFID Reader 11 Execute Command', True)
    ]
    requests.put(PUT_ADDR, json=tuple_to_gavno(base))
    await asyncio.sleep(TICK_DELAY)
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
    await asyncio.sleep(TICK_DELAY)
    base = [
        ('RFID In Execute Command', False)
    ]
    put(base)
    await asyncio.sleep(TICK_DELAY)
    ans = get(['RFID In Read Data'])
    if ans[0]['value'] <= 108:
        put([('CT 1 (+)', False),('CT 1 Left', True),('CT 1A Right', True)])
        sklad1_move = True
        if len(PLAN):
            asyncio.create_task(spawn_item(2, 2, PLAN.pop(0)))
    else:
        put([('StopR 1 Out', False)])
        if len(PLAN):
            asyncio.create_task(spawn_item(3, 2, PLAN.pop(0)))


async def sklad1_leave(new_value):
    global sklad1_move
    if not new_value or not sklad1_move:
        return
    put([('CT 1 (+)', True), ('CT 1 Left', False), ('CT 1A Right', False), ('StopR 1 Out', False)])
    sklad1_move = False


async def lock_input_a(new_value):
    global a_query, a_lock
    if not new_value:
        put([('Roller Stop Load A', True), ('Load RC A4', False), ('RC A3', False), ('Curved RC A2', False), ('RC A1', False)])
        base = [
            ('RFID A1 Command', 2),
            ('RFID A1 Memory Index', 1),
            ('RFID A1 Execute Command', True)
        ]
        put(base)
        await asyncio.sleep(TICK_DELAY)
        base = [
            ('RFID A1 Execute Command', False)
        ]
        put(base)
        await asyncio.sleep(TICK_DELAY)
        ans = get(['RFID A1 Read Data'])[0]['value']
        if ans == 0:
            put([('Roller Stop Load A', False), ('Load RC A4', True), ('RC A3', True), ('Curved RC A2', True), ('RC A1', True)])
            return
        base = [
            ('RFID A1 Command', 1),
            ('RFID A1 Execute Command', True)
        ]
        put(base)
        await asyncio.sleep(TICK_DELAY)
        base = [
            ('RFID A1 Execute Command', False)
        ]
        put(base)
        await asyncio.sleep(TICK_DELAY)
        id = get(['RFID A1 Read Data'])[0]['value']
        a_query.append({'type': 'input', 'address': ans, 'id': id})


# Callbacks Table
CALLBACKS = {
    'RS 1 In': create_new_tag,
    'CS 1': sklad1,
    'RS 1A Out': sklad1_leave,
    'At Load A': lock_input_a,
}


async def elevator_input(task, elevator):
    # Pick up
    put([(f'Forks Left {elevator}', True)])
    while not ans[f'At Left {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    put([(f'Lift {elevator}', True)])
    await asyncio.sleep(0.3)
    while ans[f'Moving Z {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    put([(f'Forks Left {elevator}', False)])
    while not ans[f'At Middle {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    # Move
    put([(f'Target Position {elevator}', math.ceil(task[f'address'] / 2))])
    await asyncio.sleep(0.6)
    while ans[f'Moving Z A'] or ans[f'Moving X A']:
        await asyncio.sleep(TICK_DELAY)
    # Place
    if task['address'] % 2:
        direction = f'Forks Left {elevator}'
    else:
        direction = f'Forks Right {elevator}'
    put([(direction, True)])
    while not ans[f'At Left {elevator}'] and not ans[f'At Right {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    put([(f'Lift {elevator}', False)])
    await asyncio.sleep(0.3)
    while ans[f'Moving Z {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    put([(direction, False)])
    while not ans[f'At Middle {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    # Move Back
    put([(f'Target Position {elevator}', 55)])
    await asyncio.sleep(0.6)
    while ans[f'Moving Z {elevator}'] or ans[f'Moving X {elevator}']:
        await asyncio.sleep(TICK_DELAY)


async def elevator_output(task, elevator):
    # Move to pick
    put([('Target Position A', task['address'] % 54)])
    await asyncio.sleep(0.6)
    while ans['Moving Z A'] or ans['Moving X A']:
        await asyncio.sleep(TICK_DELAY)
    # Pick
    if task['address'] % 2:
        direction = 'Forks Left A'
    else:
        direction = 'Forks Right A'
    put([(direction, True)])
    while not ans['At Left A'] and not ans['At Right A']:
        await asyncio.sleep(TICK_DELAY)
    put([('Lift A', True)])
    await asyncio.sleep(0.3)
    while ans['Moving Z A']:
        await asyncio.sleep(TICK_DELAY)
    put([(direction, False)])
    while not ans['At Middle A']:
        await asyncio.sleep(TICK_DELAY)
    # Move Back
    put([('Target Position A', 55)])
    await asyncio.sleep(0.6)
    while ans['Moving Z A'] or ans['Moving X A']:
        await asyncio.sleep(TICK_DELAY)
    put([('Forks Right A', True)])
    while not ans['At Right A']:
        await asyncio.sleep(TICK_DELAY)
    put([('Lift A', False)])
    await asyncio.sleep(0.3)
    while ans['Moving Z A']:
        await asyncio.sleep(TICK_DELAY)
    put([('Forks Right A', False)])
    while not ans['At Middle A']:
        await asyncio.sleep(TICK_DELAY)


# Cycled routines
async def a_routine():
    global a_lock, a_query, ans
    if a_lock or len(a_query) == 0:
        return
    a_lock = True
    task = a_query.pop(0)
    print(f'Starting task {task}')
    if task['type'] == 'input':
        await elevator_input(task, 'A')
        put([('Roller Stop Load A', False), ('Load RC A4', True), ('RC A3', True), ('Curved RC A2', True), ('RC A1', True)])
    elif task['type'] == 'output':
        await elevator_output(task, 'A')
    a_lock = False


async def b_routine():
    global b_lock, b_query, ans
    if b_lock or len(b_query) == 0:
        return
    b_lock = True
    task = b_query.pop(0)
    print(f'Starting task {task}')
    if task['type'] == 'input':
        await elevator_input(task, 'B')
        put([('Roller Stop Load B', False), ('Load RC B3', True)])
    elif task['type'] == 'output':
        await elevator_output(task, 'B')
    b_lock = False


# Routines
async def spawn_item(part, base, address):
    global in_query
    in_query.add(address)
    base = [
        ('Emitter 1 (Part)', part),
        ('Emitter 1 (Base)', base),
        ('Emitter 1 (Emit)', True),
    ]
    put(base)
    await asyncio.sleep(0.1)
    stop = [
        ('Emitter 1 (Emit)', False),
    ]
    put(stop)


def tuple_to_gavno(tuple_list):
    return [{'name':i[0],'value':i[1]} for i in tuple_list]


# Startup
def run_rollers():
    base = [
        ('RC (4m) 1.1', True),
        ('CT 1 (+)', True),
        ('RC A1', True),
        ('Curved RC A2', True),
        ('RC A3', True),
        ('Load RC A4', True),
        ('RC (6m) 1.2', True),
        ('Unload RC A5', True),
        ('RC A6', True),
        ('CT A (+)', True),
        ('RC A7', True),
        ('CT B (+)', True),
        ('RC B2', True),
        ('Load RC B3', True),
        ('Unload RC B4', True),
        ('RC B5', True),
        ('Curved RC B6', True),
        ('RC B7', True),
        ('RC A8', True),
        ('RC B1', True),
        ('RC (2m) 1.3', True),
        ('RC (2m) 1.4', True),
        ('RC (6m) 1.5', True),
        ('RC (2m) 1.6', True),
        ('RC (4m) 1.7', True),
        ('RC B10', True),
    ]
    requests.put(PUT_ADDR, json=tuple_to_gavno(base))


ans_old = False
ans = {}


async def main_cycle():
    global ans_old, ans
    base = [
        "RS 1 In",
        "RFID In Read Data",
        "CS 1",
        "CS 1A",
        "RS 1A Out",
        "RFID A1 Read Data",
        "At Load A",
        "At Right A",
        "At Middle A",
        "At Left A",
        "Moving Z A",
        "Moving X A",
        "At Load B",
        "At Right B",
        "At Middle B",
        "At Left B",
        "Moving Z B",
        "Moving X B",
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
        asyncio.create_task(CALLBACKS[i[0]](i[1]))
    ans_old = ans
    asyncio.create_task(a_routine())


def put(base):
    return requests.put(PUT_ADDR, json=tuple_to_gavno(base)).json()


def get(base):
    return requests.get(GET_ADDR, json=base).json()


async def main_loop():
    while True:
        await main_cycle()
        await asyncio.sleep(0.1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(spawn_item(1,2,1))
    run_rollers()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_loop())
