fin = open("signed.txt",'r')

with fin as f:
    content = f.readlines()


for c in content:
    str = c.split()
    if len(str)==16:

            print(str[10])