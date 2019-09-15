import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta

x=np.arange(0,5)
y=np.arange(2,7)+np.random.randn(5)

x2=np.arange(0,5)
y2=np.arange(2,7)+np.random.randn(5)

plt.plot(x, y, label='First Series')
plt.plot(x2, y2, label='Second Series')
plt.xlabel('Test x')
plt.ylabel('Test y')
plt.title('Title Test')
plt.legend()
plt.show()


x = [2,4,6,8,10]
y = [4,6,7,7,3]

x2 = [2.6,4.4,6.1,8.25,10.9]
y2 = [4.32,4,2.5,7.6,3.36]

plt.bar(x,y,label='bars1', color = 'r')
plt.bar(x2,y2,label='bars2', color = 'c')
plt.legend()

population_ages = np.random.randint(0,130,20).tolist()
ids = [x for x in range(len(population_ages))]
plt.bar(ids,population_ages)

bins = np.arange(0,140,10).tolist()
plt.hist(population_ages, bins, histtype='bar',rwidth=0.9)

plt.scatter(x2,y2, label='sp1', color='g',marker='*',s=200)
plt.scatter(x,y, label='sp0', color='b',s=150)
plt.grid()
plt.legend()

days = [x+1 for x in list(range(5))]
a1 = [1,2,1,2,3]
a2 = [3,2,7,8,9]
a3 = [10,5,2,1,3]

plt.stackplot(days, a1, a2, a3, colors=['m','c','r'] )
plt.plot([],[],color='m',label='a1', linewidth=5)
plt.plot([],[],color='c',label='a2', linewidth=5)
plt.plot([],[],color='r',label='a3', linewidth=5)
plt.legend()

slices = [7,2,2,12]
activities = [f'a{x}' for x in range(len(slices))]
plt.pie(slices, labels=activities, colors=['g','m','c','r'], startangle=90, 
        shadow=True)

plt.pie(slices, labels=activities, colors=['g','m','c','r'], startangle=90, 
        shadow=True, explode = (0,0.2,0,0), autopct='%2.2f%%')

days = pd.date_range(datetime.now(),datetime.now()+timedelta(days=10))
y = np.random.randn(len(days)).tolist()
plt.scatter(days,y) # does not work

# get a reference to the plot
fig = plt.figure()
subplot1 = plt.subplot2grid((1,1),(0,0)) # a reference to the 1 by 1 sub plot...
subplot1.plot_date(days,y, label='byday')
subplot1.grid(color='g',linestyle='dotted')
for label in subplot1.xaxis.get_ticklabels():
    label.set_rotation(45)
fig.legend()
fig.subplots_adjust(left=0.09,right=0.94, bottom=0.2,top=0.9,wspace=0.2,hspace=0.0)
fig.show()







