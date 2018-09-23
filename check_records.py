from pymongo import MongoClient

if __name__ == '__main__':
    earliest = 7804800
    count = 0
    client = MongoClient('localhost', 27017)
    db = client.darksky
    collection = db.pastCurrentConditions
    cursor = collection.find({}).sort("time",1)
    #make a list of each document that doesn't have a time greater than 3600 from the last record
    gap_list = []
    prior_time = 7801200
    print("STARTING TIME", prior_time)
    # for document in cursor:
    #     print("beginning of for loop, count is",count)
    #     if count > 0:
    #         if document["time"] != (prior_time + 3600):
    #             print("DOC TIME (IN THE IF LOOP)",document["time"])
    #             print("prior time plus 3600",str((prior_time + 3600)))
    #             gap_list.append(document)
    #             #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    #             #print(document)
    #             #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    #     prior_time = document["time"]
    #     print("SET the prior_time by document time", prior_time)
    #     count +=1
    #     print("count is now",count)

    for document in cursor:
        if document["time"] != (prior_time + 3600):
            print("DOC TIME",document["time"])
            print("prior time plus 3600",str((prior_time + 3600)))
            gap_list.append(document)
            print(document["_id"])
        # else:
        #     print("ok",document["time"])
        prior_time = document["time"]
        #print("SET the prior_time by document time", prior_time)