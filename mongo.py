#!/usr/bin/python3.5
import pymongo
from pprint import pprint

##  Client connection to remote mongodb
##  format: mongodb://<Username>:<password>@<Remote_server_ip>/<Database_name>
##        or mongodb://localhost:27017/ for local database connection

##  Set REMOTE access remote db from Sparkit server
REMOTE=False
client=None

if REMOTE:
    print("Accessing Remote Database server")
    #pattern :mongodb://<dbusername>:<dbPassword>@<IP / Machinename >
    client = pymongo.MongoClient("mongodb://root:root123@KOR1099834") # defaults to port 27017
else:
    print("Accessing Host system Database server")
    client = pymongo.MongoClient("mongodb://localhost:27017/")

##   param dbName should be a string argument
def CheckIfDatabaseExists(dbName):
    dblist = client.list_database_names()
    if dbName in dblist:
        print("The database exists.")
        print("Existing Database list:",client.list_database_names())
        return True
    else:
        print("The database does'nt exists.")
        return False

##   param collectionName should be a string argument
def CheckIfCollectionExists(dbObj,collectionName):
    if dbObj is not None:
        collist = dbObj.list_collection_names()
        if collectionName in collist:
##            print("The collection exists.")
            return True
        else:
##            print("The collection does'nt exists.")
            return False

def CreateDB(dbName):
    dbObj=client[dbName]
##    print("Creation of DB {} successful".format(dbName))
    return dbObj

def CreateCollection(dbObj,collName):
    if dbObj is not None:
        colObj=dbObj[collName]
##        print("Creation of collection {} successful".format(collName))
        return colObj

##   e.g contentDict={ "name": "John", "address": "123 industrial area" }
def InsertIntoCollection(collobj,contentDict):
    if collobj is not None:
        insertId=collobj.insert_one(contentDict)
        # To access insertId use insertId.inserted_id
        return insertId


##  e.g
##  contentDictList = [
##      { "name": "Amy", "address": "Apple st 652"},
##      { "name": "Hannah", "address": "Mountain 21"},
##      { "name": "Michael", "address": "Valley 345"}]

##  Also to insert with specified id's you can use the following format
##  contentDictList = [
##      { "_id": 1, "name": "John", "address": "Highway 37"},
##      { "_id": 2, "name": "Peter", "address": "Lowstreet 27"},
##      { "_id": 3, "name": "Amy", "address": "Apple st 652"}]
def InsertMultiIntoCollection(collObj,contentDictList):
    if collObj is not None:
        insertIds=collObj.insert_many(contentDictList)
        # To access insertId use insertIds.inserted_ids
        return insertIds

##  To find first document in given collection and print the same
def FindOne(collObj): #extra param dbName added by eru5kor
    if collObj is not None:  
        print(collObj.find_one())
        returncollObj.find_one()

##  Return all documents in the given collection, and print each document (equivalent to SELECT * in MySQL.)
##  e.g for select
##  select = { "address": "Lowstreet 27" }
##  select = { "address": { "$gt": "B" } } "address" field starts with the letter "B" or higher (alphabetically)
##  select = { "address": { "$regex": "^H"  } } "address" field starts with the letter "H"
def Find(collObj,target,select=None):
    if collObj is not None:
        if select==None:
##            for x in collObj.find(target):
##                print(x)
            return collObj.find(target)
        else:            
##            for x in collObj.find(target,select):
##                print(x)
            return collObj.find(target,select)

##  sort elements of find according to param (string expected) , option is for ascending or decending sort
##      ascending = 1
##      descending = -1
def Sort(findobj,param,option=None):
    if findobj is not None:
        if option!=None:
            return findobj.sort(param,option)
        else:
            return findobj.sort(param,1)

##   deletes the first occurance of the given queryDict
##   e.g queryDict = { "address": "Mountain 21" } Delete the document with the address "Mountain 21"
def DeleteOne(collObj,queryDict):
    if (collObj is not None ) and queryDict!={}:
        collObj.delete_one(queryDict)


##  To delete more than one document, we use the deleteMany() method
##  queryDict = { "address": {"$regex": "^S"} } Delete all documents were the address starts with the letter S
##  queryDict = { } Delete all documents in the given collection
def DeleteMany(collobj,queryDict):
    if collobj is not None:
        collobj.delete_many(queryDict)

##  Delete enire collection/table
def DropCollection(collObj):
    if collObj is not None:
        collObj.drop()

##  update contents of given collection
##  target={ "address": "Valley 345" }
##  value={ "address": "Canyon 123" } 
##  Change the address from "Valley 345" to "Canyon 123"
        
def UpdateOne(collObj,target,value):
    if collObj is not None :#and collObj.count_documents({"name":value["name"]})==0:
        collObj.update_one(target, { "$set": value },upsert=True)
#    else:
#        print ("Entry Exists")

##  To update all documents that meets the criteria of the query
##  myquery = { "address": { "$regex": "^S" } }
##  newvalues = { "$set": { "name": "Minnie" } } 
def UpdateMany(collObj,target,value):
    if collObj is not None:
        collObj.update_many(target,{ "$set": value },upsert=True)

##  limit elements to given limit
##  if limit=5 then it limits the result to only return 5 documents
def limit(collObj,limit):
    return mycol.find().limit(limit)

##  Sample main method to test usage         
def main():
    collobj=CreateCollection(CreateDB("admin"),"TOPAS")
    
        
    #pprint(CreateDB("admin").collection_names(include_system_collections=False))
    #insertId=InsertIntoCollection(collobj,{})


if __name__ == '__main__':
	main()

