Red Queen
=========

Red Queen is framework that allows the connection between many disjointed application endpoints, using an authentication
scheme, so that an interconnected network of triggers and capabilities is formed. Basically, Red Queen receives 
triggers from applications and routes them to specific action endpoints, regardless of the application type or 
language.

Example Message
--------------
```
curl --request POST \
  --url https://crump.space/rq-dev/api/v1.0/messages \
  --header 'content-type: application/json' \
  --data '{\n    "type":"command",\n    "key":"1234567890gggd",\n    "destination":"rqirc",\n    "data":{\n        "channel":"##rqtest",\n        "isaction":false,\n        "message":"test!"\n    }\n}'
```
