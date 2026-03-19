#map() and filter()
lst=[1,2,3,4,5]
def ers(n):
    return n%2==0
def ers2(x):
    return x*2

r=map(ers2,list(filter(ers,lst)))
print(list(r))# result:[4, 8]

#map()
def mp(s):
    return s*3
d=map(mp,lst)
print(list(d)) # result:[3, 6, 9, 12, 15]

#filter()
def fil(n):
    return n%2==0
a=filter(fil,lst)
print(list(a))# result:[2, 4]

#reduce()
from functools import reduce

nums = [1, 2, 3, 4, 5]

def add(x, y):
    return x + y

total = reduce(add, nums)
print(total) # result: 15 ->sum of all numbers

