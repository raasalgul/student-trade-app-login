from flask import request
from userLogin import app
import boto3
import logging
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from datetime import datetime
import json

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS dynamo db '''
dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))
''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
table_name = os.getenv("DYNAMO_USER_TABLE")

'''signUp method will add a record to AWS Cognito and then add those info to User Info Dynamo DB, before
adding to the cognito we will do a check if the email id is already present in the dynamo DB'''


@app.route('/sign-up', methods=['POST'])
def signUp():
    logging.log("signUp() request is "+json.dumps(request.get_json()))
    response = None
    try:
        '''Connect to the User Info table'''
        table = dynamoDbResource.Table(table_name)
        logging.log("Table is connected")
        '''email is the primary key and institution is the sort key'''
        key = {"email": request.json['email'],
               "institution": request.json['institution']
               }
        item = {"name": request.json['username'],
                "email": request.json['email'],
                "institution": request.json['institution'],
                "added_datetime":datetime.now(),
                "updated_datetime":datetime.now()
                }
        response = table.get_item(Key=key)
        logging.log("Is already existed user {}".format('Item' in response))
        ''''Checking for email is already present in the application (by checking user info table)'''
        if 'Item' not in response:
            try:
                '''If the email is not already in the db add it to the cognito pool'''
                response = cognitoClient.sign_up(
                    ClientId=os.getenv('COGNITO_CLIENT_API'),
                    Username=request.json['email'],
                    Password=request.json['password'],
                    UserAttributes=[{"Name": "name", "Value": request.json['username']}
                                    ],
                )
                logging.log("User added to Cognito Pool {}".format(response))
                '''After adding to the cognito pool add the basic info to user info table'''
                table.put_item(Item=item)
                logging.log("New User added to the Dynamo Db")
            except ClientError as e:
                logging.error(e)
    except ClientError as e:
        logging.error(e)
    return response
