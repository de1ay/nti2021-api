import asyncio
import math
from time import sleep

import aiohttp
import requests

# Storage specs 6x9=54 x2=108 x2=216


PUT_ADDR = 'http://localhost:7410/api/tag/values/by-name'
GET_ADDR = 'http://localhost:7410/api/tag/values/by-name'
TICK_DELAY = 0.06
PLAN = [1,2,3,0,109,110,111]
# Query
in_query = set()
a_query = list()
b_query = list()
# Semaphores
sklad1_move = False
a_lock = False
b_lock = False
central_lock = False


# Callbacks
async def create_new_tag(new_value):
    if not new_value:
        return
    base = [
        ('RFID Reader 11 Command', 1),
        ('RFID Reader 11 Execute Command', True)
    ]
    await put(base)
    await asyncio.sleep(TICK_DELAY)
    base = [
        ('RFID Reader 11 Execute Command', False)
    ]
    await put(base)
    await asyncio.sleep(TICK_DELAY)
    ans = await get(['RFID Reader 11 Read Data'])
    ans = ans[0]['value']
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
    await put([('StopR 1 Out', True)])
    base = [
        ('RFID In Command', 2),
        ('RFID In Memory Index', 1),
        ('RFID In Execute Command', True)
    ]
    await put(base)
    await asyncio.sleep(TICK_DELAY)
    base = [
        ('RFID In Execute Command', False)
    ]
    await put(base)
    await asyncio.sleep(TICK_DELAY)
    ans = await get(['RFID In Read Data'])
    if 0 < ans[0]['value'] <= 108:
        await put([('CT 1 (+)', False),('CT 1 Left', True),('CT 1A Right', True)])
        sklad1_move = True
        if len(PLAN):
            asyncio.create_task(spawn_item(2, 2, PLAN.pop(0)))
    else:
        await put([('StopR 1 Out', False)])
        if len(PLAN):
            asyncio.create_task(spawn_item(3, 2, PLAN.pop(0)))


async def sklad1_leave(new_value):
    global sklad1_move
    if not new_value or not sklad1_move:
        return
    await put([('CT 1 (+)', True), ('CT 1 Left', False), ('CT 1A Right', False), ('StopR 1 Out', False)])
    sklad1_move = False


async def lock_input_a(new_value):
    global a_query, a_lock
    if not new_value:
        await put([('Roller Stop Load A', True), ('Load RC A4', False), ('RC A3', False), ('Curved RC A2', False), ('RC A1', False)])
        base = [
            ('RFID A1 Command', 2),
            ('RFID A1 Memory Index', 1),
            ('RFID A1 Execute Command', True)
        ]
        await put(base)
        await asyncio.sleep(0.6)
        base = [
            ('RFID A1 Execute Command', False)
        ]
        await put(base)
        await asyncio.sleep(TICK_DELAY)
        ans = await get(['RFID A1 Read Data'])
        print(ans)
        ans = ans[0]['value']
        if ans == 0:
            await put([('Roller Stop Load A', False), ('Load RC A4', True), ('RC A3', True), ('Curved RC A2', True), ('RC A1', True)])
            return
        base = [
            ('RFID A1 Command', 1),
            ('RFID A1 Execute Command', True)
        ]
        await put(base)
        await asyncio.sleep(TICK_DELAY)
        base = [
            ('RFID A1 Execute Command', False)
        ]
        await put(base)
        await asyncio.sleep(TICK_DELAY)
        id = await get(['RFID A1 Read Data'])
        id = id[0]['value']
        a_query.append({'type': 'input', 'address': ans, 'id': id})


async def lock_input_b(new_value):
    global b_query, b_lock
    if not new_value:
        await put([('RC B2', False), ('Load RC B3', False)])
        base = [
            ('RFID B1 Command', 2),
            ('RFID B1 Memory Index', 1),
            ('RFID B1 Execute Command', True)
        ]
        await put(base)
        await asyncio.sleep(0.6)
        base = [
            ('RFID B1 Execute Command', False)
        ]
        await put(base)
        await asyncio.sleep(TICK_DELAY)
        ans = await get(['RFID B1 Read Data'])
        ans = ans[0]['value']
        if ans == 0:
            await put([('RC B2', True), ('Load RC B3', True)])
            return
        base = [
            ('RFID B1 Command', 1),
            ('RFID B1 Execute Command', True)
        ]
        await put(base)
        await asyncio.sleep(TICK_DELAY)
        base = [
            ('RFID B1 Execute Command', False)
        ]
        await put(base)
        await asyncio.sleep(TICK_DELAY)
        id = await get(['RFID B1 Read Data'])
        id = id[0]['value']
        b_query.append({'type': 'input', 'address': ans, 'id': id})


async def central_b_path(new_value):
    global central_lock
    if not new_value:
        return
    await put([('StopR 2 In', True), ('CT 2 (+)', False), ('RC (2m) 1.3', False)])
    while central_lock:
        await asyncio.sleep(TICK_DELAY)
    central_lock = 'b'
    await put([('CT 2 Left', True), ('CT 2A Right', True)])


async def central_out(new_value):
    if not central_lock:
        return
    if central_lock == 'b' and new_value:
        return
    elif central_lock == 'a' and new_value:
        return
    await put([('CT 2A Right', False),
               ('CT 2A Left', False),
               ('CT 2 Left', False),
               ('CT 2 Right', False),
               ('CT 2 Left', False),
               ('StopR 2 In', False),
               ('CT 2 (+)', True)])


async def central_a_path(new_value):
    global central_lock
    if new_value:
        return
    if central_lock:
        await put([('StopR 2A In from A', True), ('RC A8', False)])
        while central_lock or not ans['RS 2 In']:
            await asyncio.sleep(1)
        await put([('StopR 2A In from A', False), ('RC A8', True)])
    central_lock = 'a'
    await asyncio.sleep(0.4)
    await put([('StopR 2 In', True), ('CT 2A Left', True), ('RC (2m) 1.3', False)])


async def central_unlock(new_value):
    global central_lock
    if central_lock and new_value:
        central_lock = False
    await put([('RC (2m) 1.3', True)])


async def central2_split(new_value):
    if not new_value:
        return
    await put([('StopR 3B Out to A', True),
               ('RC B10', False),
               ('RFID B3 Command', 2),
               ('RFID B3 Memory Index', 1),
               ('RFID B3 Execute Command', True),
               ('CT 3B (-)', False)])
    await asyncio.sleep(TICK_DELAY)
    base = [
        ('RFID B3 Execute Command', False)
    ]
    await put(base)
    await asyncio.sleep(TICK_DELAY)
    adr = await get(['RFID B3 Read Data'])
    if adr[0]['value'] != 0:
        await put([('CT 3B Right', True)])
        await asyncio.sleep(2)
        while not ans['RS 3B Out to B']:
            await asyncio.sleep(TICK_DELAY)
    else:
        await put([('CT 3B Left', True),
                   ('CT 3 Right', True)])
        while not ans['CS 3']:
            await asyncio.sleep(TICK_DELAY)
        await put([('CT 3B Left', False),
                   ('CT 3 Right', False)])
    await put([('StopR 3B Out to A', False),
               ('RC B10', True),
               ('CT 3B (-)', True),
               ('CT 3B Right', False),
               ('CT 3B Right', False)])


async def b_path_in(new_value):
    if new_value:
        return
    await put([('CT B (+)', False)])
    await asyncio.sleep(1)
    await put([('RC B1', False), ('CT B Left', True)])
    while not ans['CS B']:
        await asyncio.sleep(TICK_DELAY)
    await put([('CT B Left', False), ('CT B (+)', True)])
    await asyncio.sleep(1)
    while ans['RS B Out']:
        await asyncio.sleep(TICK_DELAY)
    await put([('RC B1', True)])


# Callbacks Table
CALLBACKS = {
    'RS 1 In': create_new_tag,
    'CS 1': sklad1,
    'RS 1A Out': sklad1_leave,
    'At Load A': lock_input_a,
    'At Load B': lock_input_b,
    'CS 2': central_b_path,
    'CS 2A': central_out,
    'CS 2A 2': central_out,
    'RS 2A In From A': central_a_path,
    'RS 2A In From B': central_unlock,
    'CS 3B': central2_split,
    'RS B In': b_path_in,
}


async def elevator_input(task, elevator):
    # Pick up
    await put([(f'Forks Left {elevator}', True)])
    while not ans[f'At Left {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    await put([(f'Lift {elevator}', True)])
    await asyncio.sleep(0.3)
    while ans[f'Moving Z {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    await put([(f'Forks Left {elevator}', False)])
    while not ans[f'At Middle {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    # Move
    if elevator == 'B':
        correction = 108
    else:
        correction = 0
    await put([(f'Target Position {elevator}', math.ceil((task['address']-correction) / 2))])
    print(f'Placing {elevator}{math.ceil((task["address"]-correction) / 2)}')
    await asyncio.sleep(0.6)
    while ans[f'Moving Z {elevator}'] or ans[f'Moving X {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    # Place
    if task['address'] % 2:
        direction = f'Forks Left {elevator}'
    else:
        direction = f'Forks Right {elevator}'
    await put([(direction, True)])
    while not ans[f'At Left {elevator}'] and not ans[f'At Right {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    await put([(f'Lift {elevator}', False)])
    await asyncio.sleep(0.3)
    while ans[f'Moving Z {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    await put([(direction, False)])
    while not ans[f'At Middle {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    # Move Back
    await put([(f'Target Position {elevator}', 55)])
    await asyncio.sleep(0.6)
    while ans[f'Moving Z {elevator}'] or ans[f'Moving X {elevator}']:
        await asyncio.sleep(TICK_DELAY)


async def elevator_output(task, elevator):
    # Move to pick
    await put([(f'Target Position {elevator}', task['address'] % 54)])
    await asyncio.sleep(0.6)
    while ans[f'Moving Z {elevator}'] or ans[f'Moving X {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    # Pick
    if task['address'] % 2:
        direction = f'Forks Left {elevator}'
    else:
        direction = f'Forks Right {elevator}'
    await put([(direction, True)])
    while not ans[f'At Left {elevator}'] and not ans[f'At Right {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    await put([(f'Lift {elevator}', True)])
    await asyncio.sleep(0.3)
    while ans[f'Moving Z {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    await put([(direction, False)])
    while not ans[f'At Middle {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    # Move Back
    await put([(f'Target Position {elevator}', 55)])
    await asyncio.sleep(0.6)
    while ans[f'Moving Z {elevator}'] or ans[f'Moving X {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    await put([(f'Forks Right {elevator}', True)])
    while not ans[f'At Right {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    await put([(f'Lift {elevator}', False)])
    await asyncio.sleep(0.3)
    while ans[f'Moving Z {elevator}']:
        await asyncio.sleep(TICK_DELAY)
    await put([(f'Forks Right {elevator}', False)])
    while not ans[f'At Middle {elevator}']:
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
        await put([('Roller Stop Load A', False), ('Load RC A4', True), ('RC A3', True), ('Curved RC A2', True), ('RC A1', True)])
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
        await put([('RC B2', True), ('Load RC B3', True)])
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
    await put(base)
    await asyncio.sleep(0.1)
    stop = [
        ('Emitter 1 (Emit)', False),
    ]
    await put(stop)


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
        ('CT 2 (+)', True),
        ('CT 2A (-)', True),
        ('CT 3B (-)', True),
        ('CT 3 (+)', True),
        ('CT 4 (+)', True),
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
        "CS 2",
        "CS 2A",
        "RS 2A In From A",
        "RS 2A In From B",
        "RS 2 In",
        "CS 2A 2",
        "CS 3B",
        "RS 3B Out to B",
        "CS 3",
        "RS B In",
        "RS B Out",
        "At Load B",
        "CS B",
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
    ans = await get(base)
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
    asyncio.create_task(b_routine())


async def put(base):
    async with aiohttp.ClientSession() as session:
        async with session.put(PUT_ADDR, json=tuple_to_gavno(base)) as response:
            return await response.json()


async def get(base):
    async with aiohttp.ClientSession() as session:
        async with session.get(GET_ADDR, json=base) as response:
            return await response.json()


async def main_loop():
    while True:
        await main_cycle()
        await asyncio.sleep(0.1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(spawn_item(1,2,112))
    run_rollers()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_loop())
