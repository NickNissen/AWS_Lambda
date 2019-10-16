import json, boto3, urllib, ENV
from botocore.exceptions import ClientError
from urllib.parse import urlparse

def lambda_handler(event, context):
	body = urllib.parse.parse_qs(event['body'])
	contactInfo = body['contact'][0]
	inquiry = body['inquiry'][0]
	print(contactInfo)
	print(inquiry)
	if sendEmail(contactInfo, inquiry):
		redirect = ENV.successURL
	else:
		redirect = ENV.failURL
	return {
		'statusCode': 302,
		'headers': {
			'location': redirect
		}
	}	
	
def sendEmail(contactInfo, inquiry):
	SENDER = ENV.sender
	RECIPIENT = ENV.recipient
	AWS_REGION = ENV.region
	WEBSITE = ENV.website
	CHARSET = 'UTF-8'
	SUBJECT = 'Website Contact Form Submission'
	BODY_TEXT = '''
		The Following Inquiry has been recieved at {}
		The contact can be reached at {}
		The details of the inquiry are:
		{}
	'''.format(WEBSITE, contactInfo, inquiry)
	client = boto3.client('ses', region_name = AWS_REGION)
	# Try to send email
	try:
		response = client.send_email(
			Destination = {
				'ToAddresses': [
					RECIPIENT
				],
			},
			Message = {
				'Body': {
					'Text': {
						'Charset': CHARSET,
						'Data': BODY_TEXT,
					},
				},
				'Subject': {
					'Charset': CHARSET,
					'Data': SUBJECT,
				},
			},
			SourceArn = ENV.sourceArn,
			ReturnPathArn = ENV.returnPathArn,
			Source = SENDER,
			ReturnPath = SENDER,
		)
	# Log an error if something goes wrong
	except ClientError as e:
		print(e.response['Error']['Message'])
		return False
	else:
		print('Email sent! Message ID:')
		print(response['ResponseMetadata']['RequestId'])
		return True
