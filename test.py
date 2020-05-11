import random

def finpos():
    return([2, 1])

agenda = [[-1, -2], [2, 1]]
agenda.append([15, 1])
agenda.append([15, 4])
if random.getrandbits(1) == 1:
    agenda.extend([[20.5, 4], [20.5, 8], finpos()])
    # self.agenda.append([20.5, 8])
    agenda.append([5, 6])
else:
    agenda.append([10.5, 4])
    agenda.append([10.5, 8])
    agenda.append([5, 6])
print(str(agenda))