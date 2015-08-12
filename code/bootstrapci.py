import random

def sample(data):
  for x in data:
    yield random.choice(data)

def bootstrapci(data,func,n=3000,p=0.95):
    index=int(n*(1-p)/2)
    r=[func(list(sample(data))) for i in range(n)]
    r.sort()
    return r[index], r[-index]

def mean(x):
    return sum(x)/len(x)


if __name__ == '__main__':
    data = [0.80696726764610904, 0.81252376300438622, 0.85538731552472702, 0.90055775771080115, 0.89766544499329926, 0.84625724686494552, 0.75323732419558742, 0.85881414581620064, 0.80899927994217202, 0.83466702339313126]

    print bootstrapci(data, mean)
