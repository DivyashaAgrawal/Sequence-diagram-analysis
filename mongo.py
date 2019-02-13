##python script with api's to access and perform opertions on mongodb
import pymongo

#Client connection to remote mongodb format: mongodb://<Username>:<password>@<Remote_server_ip>/<Database_name>
#or mongodb://localhost:27017/ for local database connection
client = pymongo.MongoClient("mongodb://root:root123@KOR1099834") # defaults to port 27017

#param dbName should be a string argument
def checkIfDatabaseExists(dbName):
    dblist = client.list_database_names()
    if dbName in dblist:
        print("The database exists.")
        return True
    else:
        print("The database does'nt exists.")
        return False

#param collName should be a string argument
def checkIfCollectionExists(dbObj,collName):
    if dbObj is not None:
        collist = dbObj.list_collection_names()
        if collName in collist:
            print("The collection exists.")
            return True
        else:
            print("The collection does'nt exists.")
            return False

def createDB(dbName):
    if collObj is not None:
        dbObj=client[dbName]
        return dbObj

def createCollection(dbObj,collName):
    if collObj is not None:
        colObj=dbObj[collName]
        return dbObj

# e.g contentDict={ "name": "John", "address": "123 industrial area" }
def insertIntoCollection(collobj,contentDict):
    if collObj is not None:
        insertId=collobj.insert_one(contentDict)
        # To access insertId use insertId.inserted_id
        return insertId


##e.g
##contentDictList = [
##  { "name": "Amy", "address": "Apple st 652"},
##  { "name": "Hannah", "address": "Mountain 21"},
##  { "name": "Michael", "address": "Valley 345"}]

##Also to insert with specified id's you can use
##mylist = [
##  { "_id": 1, "name": "John", "address": "Highway 37"},
##  { "_id": 2, "name": "Peter", "address": "Lowstreet 27"},
##  { "_id": 3, "name": "Amy", "address": "Apple st 652"}]

def insertMultiIntoCollection(collObj,contentDictList):
    if collObj is not None:
        insertIds=collobj.insert_many(contentDictList)
        # To access insertId use insertIds.inserted_ids
        return insertIds

##To find first document in given collection and the same
def findOne(collObj):
    if collObj is not None:    
        print(collObj.find_one())
        return collObj.find_one()

##Return all documents in the given collection, and print each document (equivalent to SELECT * in MySQL.)
## e.g for select
## select = { "address": "Lowstreet 27" }
## select = { "address": { "$gt": "B" } } "address" field starts with the letter "B" or higher (alphabetically)
## select = { "address": { "$regex": "^H"  } } "address" field starts with the letter "H"
def find(collObj,select=None):
    if collObj is not None:
        if select!=None:
            for x in collObj.find():
                print(x)
            return collObj.find()
        else:            
            for x in mycol.find({},select):
                print(x)
            return mycol.find({},select)

##sort elements of find according to param (string expected) , option is for ascending or decending sort
##    ascending = 1
##    descending = -1


def sort(findobj,param,option=None):
    if findobj is not None:
        if option!=None:
            return findobj.sort(param,option)
        else:
            return findobj.sort(param,1)

#deletes the first occurance of the given queryDict
# e.g queryDict = { "address": "Mountain 21" } Delete the document with the address "Mountain 21"

def deleteOne(collObj,queryDict):
    if (collObj is not None ) and queryDict!={}:
        collObj.delete_one(queryDict)


##To delete more than one document, we use the deleteMany() method
## queryDict = { "address": {"$regex": "^S"} } Delete all documents were the address starts with the letter S
## queryDict = { } Delete all documents in the given collection
def deleteMany(collobj,queryDict):
    if collobj is not None:
        collobj.delete_many(queryDict)

##Delete enire collection/table
def dropCollection(collObj):
    if collObj is not None:
        collobj.drop()

#update contents of given collection
##target={ "address": "Valley 345" }
##value={ "address": "Canyon 123" } 
##Change the address from "Valley 345" to "Canyon 123"
def updateOne(collObj,target,value):
    if collObj is not None:
        collObj.update_one(target, { "$set": value })

##To update all documents that meets the criteria of the query
##myquery = { "address": { "$regex": "^S" } }
##newvalues = { "$set": { "name": "Minnie" } } 
def updateMany(collObj,target,value):
    if collObj is not None:
        collObj.update_many(target,{ "$set": value })

##limit elements to given limit
##if limit=5 then it limits the result to only return 5 documents
def limit(collObj,limit):
    return mycol.find().limit(limit)
        
def main():
    boolval=checkIfDatabaseExists("test")


if __name__ == '__main__':
    main()

