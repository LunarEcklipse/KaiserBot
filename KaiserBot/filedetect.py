import os

absPath = os.path.abspath(__file__)
dname = os.path.dirname(absPath)
os.chdir(dname)

try:
    print(__file__)
    print(os.getcwd() + "\\response.json", 'r')
    file = open(os.getcwd() + "\\response.json", 'r')
except(FileNotFoundError) as exception:
    print("What the fuck")
print("End")
x = input()