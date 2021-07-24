from mip import Model, xsum, minimize, maximize, INTEGER, BINARY
import numpy as np
np.random.seed(9824)

# input
capacity = np.array([1000])
print('capacity\n', capacity)
consumption = np.random.randint(10, size=(7,2))
print('consumption\n', consumption)
initial_quantity = np.random.randint(10, size=2)
print('initial_quantity\n', initial_quantity)
target_remaining_quantity = np.array([10,10])
print('target_remaining_quantity\n', target_remaining_quantity)
price = np.random.randint(5, size=2)
print('price\n', price)
delivery_fee = np.array([20])
print('delivery_fee\n', delivery_fee)
volume = np.array([1,2])
print('volume\n', volume)
U = set(range(len(target_remaining_quantity)))
V = set(range(len(delivery_fee)))
W = set(range(len(consumption)))
S = set(range(len(capacity)))
T = {0,1}

model = Model()
x = [[model.add_var(var_type=INTEGER, lb=0) for j in W] for i in U]
y = [[model.add_var(var_type=BINARY, lb=-10000) for j in W] for i in V]
z = [[[model.add_var(var_type=BINARY, lb=-10000) for k in T] for j in W] for i in V]
model.objective = minimize(xsum(x[i][j] * price[i] for i in U for j in W) + xsum(y[i][j] * delivery_fee[i] for i in V for j in W))
# storage space constraint
for i in S:
    for j in W:
        model += xsum(initial_quantity[a] * volume[a] - consumption[c][a] * volume[a] + x[a][b] * volume[a] for a in U for b in W if b <= j for c in W if c < j) <= capacity[i]
# demand constraint
for i in U:
    for j in W:
        model += initial_quantity[i] + xsum(x[i][a] - consumption[a][i] for a in W if a <= j) >= 0

# if statements
for i in V:
    for j in W:
        model += 1 - y[i][j] <= 10000 * z[i][j][0]
for i in V:
    for j in W:
        model += xsum(x[a][j] for a in U) <= 10000 * (1 - z[i][j][0])

for i in V:
    for j in W:
        model += y[i][j] <= 10000 * z[i][j][1]
for i in V:
    for j in W:
        model += 1 - xsum(x[a][j] for a in U) <= 10000 * (1 - z[i][j][1])

# Safety stock constraint
for i in U:
    model += initial_quantity[i] + xsum(x[i][j] - consumption[j][i] for j in W) >= target_remaining_quantity[i]

# optimize
model.optimize()

restock_plan = np.zeros((len(target_remaining_quantity),len(consumption)))
for i in range(len(target_remaining_quantity)):
    for j in range(len(consumption)):
        restock_plan[i][j] = x[i][j].x
print('restock plan is\n', restock_plan)

delivery_plan = np.zeros((len(delivery_fee),len(consumption)))
for i in range(len(delivery_fee)):
    for j in range(len(consumption)):
        delivery_plan[i][j] = y[i][j].x
print('delivery plan is\n', delivery_plan)