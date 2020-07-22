import pulp
import itertools

import data


N = range(data.PEOPLE)
S = range(data.SECTIONS)
R = range(data.RESTRICTIONS)
M = range(data.MONTHS)

# Modelling
prob = pulp.LpProblem('Conformity', pulp.LpMaximize)

s = pulp.LpVariable.dicts('Person i is in section j', (N, S), lowBound=0, upBound=1, cat=pulp.LpInteger)
ss = pulp.LpVariable.dicts('Person i and j are in section k', (N, N, S), lowBound=0, upBound=1, cat=pulp.LpInteger)

prob += sum(s[i][j] * data.preferences[i][j] for i in N for j in S), 'Test'

# Definitory constraints
for i in N:
    prob += sum(s[i][j] for j in S) == 1
    prob += sum(s[i][j] * data.backdoor[i][j] for j in S) <= 0

for i, j, k in itertools.product(N, S, N):
    prob += s[i][j] + s[k][j] - ss[i][k][j] <= 1

# Relaxable constraints
for j in S:
    prob += sum(s[i][j] for i in N) >= data.min_people[j]
    prob += sum(s[i][j] for i in N) <= data.max_people[j]

    prob += sum(s[i][j] * data.sex[i] for i in N) >= data.min_male[j]
    prob += sum(s[i][j] * data.sex[i] for i in N) <= data.max_male[j]
    
    prob += sum(s[i][j] * data.rotation[i][j] for i in N) >= data.min_rotation[j]
    prob += sum(s[i][j] * data.rotation[i][j] for i in N) <= data.max_rotation[j]

    prob += sum(s[i][j] * data.experience[i][j] for i in N) >= data.min_experience[j]

    prob += sum(s[i][j] * data.leader[i][j] for i in N) >= data.min_leader[j]

    prob += sum(s[i][j] * (data.commitement[i] - data.min_commitement) for i in N) >= 0

    for k in M:
        prob += sum(s[i][j] * data.disponibility[i][k] for i in N) >= data.min_disponibility[j]
    
    for i in N:
        prob += sum(ss[i][k][j] * data.incompatibility[i][k] for k in N) <= 0

prob.writeLP
prob.solve()
print(pulp.value(prob.objective))
for i, j in itertools.product(N, S):
    if s[i][j].value():
        print(f'{i + 1} in section {j + 1}')