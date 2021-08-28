"""
This script can be used to optimize restocking times and quantities for a storage or a facility.
Suppose that we have a storage for multiple types of item, and it's an intermediary node within a supply chain. The 
items stored at this storage will be transported or consumed daily and we can arrange restocking delivery from the 
upstream suppliers. However, each item has a cost and each delivery has a cost as well. What we want to do is to 
optimize the restocking times and quantities so that the total cost is minimized.
"""

from mip import Model, xsum, minimize, INTEGER, BINARY
import numpy as np
np.random.seed(9824)

# input of mathematical model

# storage space volume
capacity = np.array([200])
print('capacity\n', capacity)

# scheduled consumption of every items. index = [x,y] = [day,item]
consumption = np.full((100,2),10)
print('consumption\n', consumption)

# initial quantity of every item. index = [x] = [item]
initial_quantity = np.full((2),0)
print('initial_quantity\n', initial_quantity)

# safety stocks of each item. default values are 10s
safety_stock = np.full((2),0)
print('safety_stock\n', safety_stock)

# prices of each item
price = np.array([1,2])
print('price\n', price)

# delivery fee. default value is 20
delivery_fee = np.array([20])
print('delivery_fee\n', delivery_fee)

# volume of each item. default values are 1 and 2 for two items respectively
volume = np.array([1,2])
print('volume\n', volume)

# set of indexes of all items
items = set(range(len(safety_stock)))

# set of indexes of all suppliers
suppliers = set(range(len(delivery_fee)))

# W is set of indexes of all days
days = set(range(len(consumption)))

# S is set of indexes of all types of storage(dry, cooler, freezer)
storages = set(range(len(capacity)))

"""
T is set of indexes of all ancillary binary variable for if-else statements.
There are two pair of if-else statements, so there are two indexes
"""
T = {0,1}

# initialize a model
model = Model()

# x is purchased quantity of every item on every day
x = [[model.add_var(var_type=INTEGER, lb=0) for day in days] for item in items]
# y is delivery plan of every supplier on every day
y = [[model.add_var(var_type=BINARY, lb=0) for day in days] for supplier in suppliers]
# z is an ancillary binary variable for if-else statement
z = [[[model.add_var(var_type=BINARY, lb=0) for k in T] for day in days] for supplier in suppliers]

# objective function is to minimize total cost which is a sum of purchase cost and delivery cost
model.objective = minimize(xsum(x[item][day] * price[item] for item in items for day in days) + xsum(y[supplier][day] * delivery_fee[supplier] for supplier in suppliers for day in days))

# storage space constraint
for storage in storages:
    for day in days:
        model += xsum(initial_quantity[item] * volume[item] for item in items) + xsum(volume[item] * x[item][delivery_day] for item in items for delivery_day in days if delivery_day <= day) - xsum(volume[item] * consumption[consumption_day][item] for item in items for consumption_day in days if consumption_day < day) <= capacity[storage]


# demand constraint. demand of each item must be covered by available quantity of the item at the beginning of each day
for item in items:
    for day in days:
        model += initial_quantity[item] + xsum(x[item][day_past] - consumption[day_past][item] for day_past in days if day_past <= day) >= 0

# if statements
for supplier in suppliers:
    for day in days:
        model += 1 - y[supplier][day] <= 100000 * z[supplier][day][0]

for supplier in suppliers:
    for day in days:
        model += xsum(x[item][day] for item in items) <= 100000 * (1 - z[supplier][day][0])

for supplier in suppliers:
    for day in days:
        model += y[supplier][day] <= 100000 * z[supplier][day][1]

for supplier in suppliers:
    for day in days:
        model += 1 - xsum(x[item][day] for item in items) <= 100000 * (1 - z[supplier][day][1])

# Safety stock constraint
for item in items:
    model += initial_quantity[item] + xsum(x[item][day] - consumption[day][item] for day in days) >= safety_stock[item]

# optimize
model.optimize()

restock_plan = np.zeros((len(safety_stock),len(consumption)))
for i in range(len(safety_stock)):
    for j in range(len(consumption)):
        restock_plan[i][j] = x[i][j].x
print('restock plan is\n', restock_plan,'\neach integers is number of a item delivered on a day')

delivery_plan = np.zeros((len(delivery_fee),len(consumption)))
for i in range(len(delivery_fee)):
    for j in range(len(consumption)):
        delivery_plan[i][j] = y[i][j].x
print('\ndelivery plan is\n', delivery_plan,'\n0 means there is no delivery on this day. 1 means there is delivery on this day')
