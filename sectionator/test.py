import pulp
import itertools
import sys


def read_graph_sys():
    args = input().split()
    while args[0] == 'c':
        args = input().split()

    n = int(args[2])
    e = int(args[3])
    i = 0
    rv = [[0 for _ in range(n)] for _ in range(n)]

    while i < e:
        args = input().split()
        if args[0] == 'c':
            continue
    
        u = int(args[0]) - 1
        v = int(args[1]) - 1
        rv[u][v] = 1
        rv[v][u] = 1
        i += 1

    return rv, n

E, n = read_graph_sys()
V = range(n)


prob = pulp.LpProblem('Treedepth', pulp.LpMinimize)

r = pulp.LpVariable.dicts('Vertice i is the root', V, lowBound=0, upBound=1, cat=pulp.LpInteger)
p = pulp.LpVariable.dicts('Vertice i is parent of vertice j', (V, V), lowBound=0, upBound=1, cat=pulp.LpInteger)
a = pulp.LpVariable.dicts('Vertice i is ancestor of vertice j', (V, V), lowBound=0, upBound=1, cat=pulp.LpInteger)
d = pulp.LpVariable('Depth of the decomposition', 0)


prob += d, 'Depth of the treedepth-decomposition, to minimize'


prob += sum(r[i] for i in V) == 1                           # One root in the tree

for j in V:
    prob += sum(p[i][j] for i in V) == 1 - r[j]             # Only one parent per vertice, except the root, which has no parent
    prob += a[j][j] == 0                                    # Cant be ancestor of itself
    prob += d >= sum(a[i][j] for i in V)                    # Depth is greater than the sum of the ancestors of every vertex

for i, j in itertools.product(V, V):
    prob += p[i][j] <= a[i][j]                              # If i is parent of j, i is ancestor of j
    prob += a[i][j] + a[j][i] <= 1                          # If i is ancestor of j, j cant be ancestor of i

for i, j, k in itertools.product(V, V, V):
    if i == j or i == k or j == k:                          
        continue
    prob += a[i][j] + a[j][k] <= a[i][k] + 1                # If i is ancestor of j, and j is ancestor of k, i is ancestor of k
    prob += a[i][j] + a[k][j] <= a[i][k] + a[k][i] + 1      # If i is ancestor of j, and k is ancestor of j, then either i is ancestor of k or k is ancestor of i
    prob += p[i][j] + p[i][k] <= 2 - a[j][k]                # Siblings can't have ancestor relationships

for i, j in itertools.product(V, V):
    prob += a[i][j] + a[j][i] >= E[i][j]                    # If there is an edge in the original graph, there is an ancestor relationship in the new graph


prob.writeLP("Treedepth.lp")

prob.solve()


rv = [str(0) for _ in range(n)]
for i, j in itertools.product(V, V):
    if p[i][j].value():
        rv[j] = str(p[i][j].value())
        #rv[j] = str(i + 1)

rv = [str(1 + int(d.value()))] + rv
rv = '\n'.join(rv)


print(prob.constraints)