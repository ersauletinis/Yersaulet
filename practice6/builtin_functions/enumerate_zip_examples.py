#enumerate() and zip()
name=["Hamilton","Max","Leclerc","Kimi"]
number=[44,3,16,12]
for i,(name,number) in enumerate(zip(name,number)):
    print(i,name,number)

#enumerate()
a=["Alonso","Norris","Piastri"]
for i,s in enumerate(a):
    print(i,s) 

#zip()
v=["Alice","Tom","Bob"]
x=["12","13","14"]
for e,a in zip(v,x):
    print(e,a)


