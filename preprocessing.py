import argparse
import os
import warnings
import re

# Import PuLP modeller functions
from pulp import *

layout = [  [2,0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,4,4,0,0,4,4,0,0,4,4,0,0,4,4,0,0],
            [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],
            [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],
            [0,0,4,4,0,0,4,4,0,0,4,4,0,0,4,4,0,0],
            [0,0,4,4,0,0,4,4,0,0,4,4,0,0,4,4,0,0],
            [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],
            [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],
            [0,0,4,4,0,0,4,4,0,0,4,4,0,0,4,4,0,0],
            [0,0,4,4,0,0,4,4,0,0,4,4,0,0,4,4,0,0],
            [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],
            [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],
            [0,0,4,4,0,0,4,4,0,0,4,4,0,0,4,4,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

# layout = [  [2,0,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
#             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
#             [0,0,4,4,0,0,4,4,0,0,4,4,0,0,4,4,0,0],
#             [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],
#             [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],
#             [0,0,4,4,0,0,4,4,0,0,4,4,0,0,4,4,0,0],
#             [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

layout_width, layout_length = len(layout), len(layout[0])

Nodes, nodeData, Arcs, arcData = [], {}, [], {}
for row in range(layout_width):
    for col in range(layout_length):
        coord = str(row)+"-"+str(col)

        if layout[row][col] == 0 :
            # path for vehicle
            Nodes.append(coord)
            nodeData[coord] = [0,0]
 
        elif layout[row][col] == 4 :
            # coord to unload carried goods
            print("DEMAND", coord, str(0), str(row+col+2))
            Nodes.append(coord)
            nodeData[coord] = [0,row+col+2]
        
        elif layout[row][col] == 2 :
            # coord vehicle to load carried goods
            print("SUPPLY", coord, 500, 0)
            Nodes.append(coord)
            nodeData[coord] = [500,0]


        if layout[row][col] not in [1,3]:
            if row+1 < layout_width:
                if layout[row+1][col] not in [1,3]:
                    coord_up = str(row+1)+"-"+str(col)
                    Arcs.append(tuple([coord,coord_up]))
                    arcData[tuple([coord,coord_up])] = [1,0,500]

            if row-1 > 0:
                if layout[row-1][col] not in [1,3]:
                    coord_down = str(row-1)+"-"+str(col)
                    Arcs.append(tuple([coord,coord_down]))
                    arcData[tuple([coord,coord_down])] = [1,0,500]

            if col+1 < layout_length:
                if layout[row][col+1] not in [1,3]:
                    coord_right = str(row)+"-"+str(col+1)
                    Arcs.append(tuple([coord,coord_right]))
                    arcData[tuple([coord,coord_right])] = [1,0,500]

            if col-1 > 0:
                if layout[row][col-1] not in [1,3]:
                    coord_left = str(row)+"-"+str(col-1)
                    Arcs.append(tuple([coord,coord_left]))
                    arcData[tuple([coord,coord_left])] = [1,0,500]


# Splits the dictionaries to be more understandable
(supply, demand) = splitDict(nodeData)
(costs, mins, maxs) = splitDict(arcData)

# Creates the boundless Variables as Integers
vars = LpVariable.dicts("Route",Arcs,None,None,LpInteger)

# Creates the upper and lower bounds on the variables
for a in Arcs:
    vars[a].bounds(mins[a], maxs[a])

# Creates the 'prob' variable to contain the problem data    
prob = LpProblem("Vehicle Routing Problem",LpMinimize)

# Creates the objective function
prob += lpSum([vars[a]* costs[a] for a in Arcs]), "Total Cost of Transport"

# Creates all problem constraints - this ensures the amount going into each node is at least equal to the amount leaving
for n in Nodes:
    prob += (supply[n]+ lpSum([vars[(i,j)] for (i,j) in Arcs if j == n]) >=
             demand[n]+ lpSum([vars[(i,j)] for (i,j) in Arcs if i == n])), "Steel Flow Conservation in Node %s"%n

# The problem data is written to an .lp file
prob.writeLP('/opt/ml/processing/data/' + 'VehicleRoutingProblem.lp')

# The problem is solved using PuLP's choice of Solver
prob.solve()

# The status of the solution is printed to the screen
print("Status:", LpStatus[prob.status])

# Each of the variables is printed with it's resolved optimum value
for v in prob.variables():
    if v.varValue > 0:
        path = re.findall(r"'(.*?)'", v.name)
        print(path[0], path[1], v.varValue)

# The optimised objective function value is printed to the screen    
print("Total Cost of Transportation = ", value(prob.objective))
