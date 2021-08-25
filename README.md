# Optimization-of-Restocking-Time-and-Quantity

This is a testing script for modeling and solving restocking time and quantity optimization problems for heterogeneous items with the following constraints:
1. initial stocks; safety stocks
2. storage space
3. demand over a time period

The goal is to minimize total cost including:
1. cost of items
2. order/delivery fee

Required inputs:
1. planning horizion with demands of items over time
2. order/delivery fee
3. volume of each type of item
4. storage space
5. item prices

Outputs:
1. optimal restock delivery time
2. optimal restock quantities
