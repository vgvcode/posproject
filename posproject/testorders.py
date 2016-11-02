#!/usr/bin/python
from __future__ import print_function # Python 2/3 compatibility
from decimal import *
import ordersmodule
import catalogmodule
import commonmodule
import sys
import time
from boto3.dynamodb.conditions import Key, Attr
import sqsmodule
import random
import json

def testCreateRemoteCatalog():
    'create a list of items and add them one by one'
    items = [
             {"itemId" : '100', "itemName": 'IDLI', "price": 20},
             {"itemId" : '101', "itemName": 'DOSA', "price": 22},
             {"itemId" : '102', "itemName": 'VADA', "price": 18},
             {"itemId" : '103', "itemName": 'POORI', "price": 25},
             {"itemId" : '104', "itemName": 'PONGAL', "price": 27},
             {"itemId" : '105', "itemName": 'CHAPPATHI', "price": 15},
             {"itemId" : '106', "itemName": 'NOODLES', "price": 20},
             {"itemId" : '107', "itemName": 'MEALS', "price": 30},
             {"itemId" : '108', "itemName": 'CHAAT', "price": 24},
             {"itemId" : '109', "itemName": 'BATURA', "price": 32}
             ]

    #create a remote catalogmodule.Catalog
    cat = catalogmodule.Catalog("SRC_CAT100", endpoint="https://dynamodb.us-east-1.amazonaws.com")
    cat.createTable()
    print('Created schema in remote db')
    
    #add items to the remote catalogmodule.Catalog
    #delay a few seconds
    print('Waiting for resource to be available...')
    time.sleep(30)
    for i in items:
        cat.addItem(i['itemId'], i['itemName'], i['price'])

def testFetchRemoteCatalog():
    cat = catalogmodule.Catalog("SRC_CAT100", endpoint="https://dynamodb.us-east-1.amazonaws.com")
    cat.fetchFromDB()
    cat.print()

def testFetchLocalCatalog():
    cat = catalogmodule.Catalog("SRC_CAT100", endpoint="http://localhost:8000")
    cat.fetchFromDB()
    cat.print()

def testFetchAllOrders(posId):
    os = ordersmodule.OrderTable()    
    r = os.fetchForPos(posId)
    for itm in r["Items"]:
        print(itm)
        print("Total orders:{}".format(len(r["Items"])))    
    
#createordersmodule.OrderQueues()

#testCreateRemoteCatalog()

#Initialization
posId = 'PosGNChettyRoadCafe'
catId = 'SRC_CAT100'
ep = "http://localhost:8000"
remoteEp = "https://dynamodb.us-east-1.amazonaws.com"

lCat = catalogmodule.Catalog(catId)

if lCat.copyFromRemote(remoteEp) == False:
    print("Remote copy failed")
    SystemExit()
    
print('Copied remote catalog to local')

items = lCat.getItems()
print(items)

"""
ct = catalogmodule.CatalogTable()
ct.deleteAllItems(catId)
"""

for i in range(1,2):
    print('Placing order number:{}'.format(i))
    o = ordersmodule.Order(posId)
    
    numItems = int(random.random() * 9 + 1)
    print("Number of items:{}".format(numItems))
    for j in range(1, numItems+1):
        itemNumStr = str(100 + int(random.random() * 10))
        itemQty = int(random.random() * 19 + 1)
        o.addItem(items[itemNumStr], itemQty)
        
    o.writeToFile("orders.txt")
     
    if o.saveToDB() == True:
        print("Order saved successfully")
    else:
        print("Order not saved")

    """
    time.sleep(10)
        
    o.addItem(items['105'], 105)
    if o.updateToDB() == True:
        print("Order updated successfully")
    else:
        print("Order not updated")
    """
    
    del o

ot = ordersmodule.OrderTable()
ot.deQueueOrdersToRemote('insert', remoteEp)
print('Dequeued all insert orders to remote DB')

"""
time.sleep(10)
ot = ordersmodule.OrderTable()
ot.deQueueOrdersToRemote('update', remoteEp)
print('Dequeued all update orders to remote DB')

o = ordersmodule.Order(posId)
orderId = "2c5f7858-9ef6-11e6-ab7c-9801a7a7a649"
o.fetchFromDB(orderId)
o.print()
o.deleteFromDB()

time.sleep(10)
ot = ordersmodule.OrderTable()
ot.deQueueOrdersToRemote('delete', remoteEp)
print('Dequeued all delete orders to remote DB')
"""

numSeconds = 6000
r = commonmodule.getOrdersMadeInXSeconds(posId, numSeconds)
listOfOrders = r['Items']
listOfOrdersByTime = sorted(listOfOrders, key=lambda order: order['Info']['CreatedTicks'])
print('Number of orders made in the last {} seconds: {}'.format(numSeconds, len(r['Items'])))
for oDict in listOfOrdersByTime:
    oObj = ordersmodule.Order(posId)
    oObj.fromDictionary(oDict)
    print("New Order:")
    oObj.print()