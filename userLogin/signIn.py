from flask import request,jsonify
from userLogin import app
import boto3
import logging
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
table_name = os.getenv("DYNAMO_USER_TABLE")



@app.route('/sign-in',methods=['POST'])
def signIn():
    logging.log("signIn() request is {}".format(request.json))
    '''Check for the user in cognito pool'''
    response = cognitoClient.initiate_auth(
        ClientId=os.getenv('COGNITO_CLIENT_API'),
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": request.json['email'], "PASSWORD": request.json['password']},
    )
    logging.log("Response from cognito {}".format(response))


    access_token = response["AuthenticationResult"]["AccessToken"]
    '''Checking whether the user in the pool'''
    responseUserData = cognitoClient.get_user(AccessToken=access_token)
    logging.log("Response user data {}".format(responseUserData))

    return jsonify(response)
