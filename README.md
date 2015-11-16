Red Queen
=========

Red Queen is framework that allows the connection between many disjointed application endpoints, using an authentication
scheme, so that an interconnected network of triggers and capabilities is formed. Basically, Red Queen receives 
triggers from applications and routes them to specific action endpoints, regardless of the application type or 
language.

Example Message
--------------
```
curl -X POST -H "Content-Type: application/json" -d '{
    "type":"command",
    "key":"1234567890gggd",
    "destination":"rqirc",
    "data":{
        "channel":"##rqtest",
        "isaction":false,
        "message":"I am a message!!"
    }
}' 'https://crump.space/rq/api/v1.0/messages'
```
