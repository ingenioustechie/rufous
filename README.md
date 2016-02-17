# rufous
### A simple Queue task with Redis and python


## Installation 
1. Checkout the repository
2. Install dependency which just `redis`

## Adding a Queue to redis
1. Import rufous
```
from rufous import rufous
``` 
2. Add @rufous decorator to your task
3. Pass the required parameter via delay method of rufous 

e.g
```
@rufous
def add(a, b):
    return a+b

add.delay(1, 4)
```
## Running a deamon
A messaging Queue requires a a deamon to watch Queue and execute it as soon as it arrives in the Queue 
You can run the this simple deamon in background with nohup as 

```
nohup python deamon.py
```

NOTE: If you are adding any new task import the same in deamon and restart the deamon. 



TODO : Complete test case for all functionality  