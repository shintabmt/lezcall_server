#!/usr/bin/python
import os
import json
from flask import Flask, request
from twilio.jwt.access_token import AccessToken, VoiceGrant
from twilio.rest import Client
import twilio.twiml
from datetime import date

ACCOUNT_SID = 'AC44502b7147c3c8885129203ba3d9e6ef'
AUTH_TOKEN = '59af58f356dc662f9a890117d0b5277d'
API_KEY = 'SKbdbd775fe2083a2faf2b2852253fa24b'
API_KEY_SECRET = 'o9dRyxNEs8hRkGXsvb7Nhr1Iybb52MqZ'
PUSH_CREDENTIAL_SID_IOS_DEV = 'CR9e7958227f6ce81726654c107a47d20d'
PUSH_CREDENTIAL_SID_IOS_PROD = 'CR8825ab010d9908c13c601bfadcb1a5a5'
PUSH_CREDENTIAL_SID_ANDROID = 'CRb0a1441bf89b5256d80328bef0950f6a'
APP_SID = 'AP32ab827c6b621bc71951397c33b2564c'
CONTACT_LIST = [{'userName': 'Phong'}, {'userName': 'Dinh'}, {'userName': 'Antony'}, {'userName': 'Khanh'}, {'userName': 'Tan'}, {'userName': 'Hiep'}]

IDENTITY = 'voice_test'
CALLER_ID = 'quick_start'

app = Flask(__name__)

@app.route('/verification', methods=['GET', 'POST'])
def verification():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)		
  		  
  client = Client(api_key, api_key_secret, account_sid)
  
  phoneNumber = request.values.get('phoneNumber')
  friendlyName = request.values.get('friendlyName')
  new_phone = client.validation_requests.create(phoneNumber, friendly_name=friendlyName)
  k = {'validation_code': str(new_phone.validation_code)}
  return json.dumps(k)

@app.route('/accessToken', methods=['GET', 'POST'])
def token():
  client_name = request.values.get('client')
  platform = request.values.get('platform')
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)
  app_sid = os.environ.get("APP_SID", APP_SID)
  
  if platform == 'iosdev':
    push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID_IOS", PUSH_CREDENTIAL_SID_IOS_DEV)
  elif platform == 'iosprod':
    push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID_IOS", PUSH_CREDENTIAL_SID_IOS_PROD)
  else:
    push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID_ANDROID", PUSH_CREDENTIAL_SID_ANDROID)
    
  if client_name:
     IDENTITY =client_name
  grant = VoiceGrant(
    push_credential_sid=push_credential_sid,
    outgoing_application_sid=app_sid
  )

  token = AccessToken(account_sid, api_key, api_key_secret, IDENTITY)
  token.add_grant(grant)
  k = {'accessToken': str(token)}
  return json.dumps(k)

@app.route('/outbound', methods=['POST'])
def outbound():
    response = twiml.Response()
    with response.dial() as dial:
        dial.number("+16518675309")
    return str(response)
  
@app.route('/outgoing', methods=['GET', 'POST'])
def outgoing():
  resp = twilio.twiml.Response()
  from_value = request.values.get('From')
  caller = request.values.get('Caller')
  caller_value=caller[7:]
  to = request.values.get('To')
  limit = request.values.get('Limit')
  bcoinUserId = request.values.get('bcoinUserId')
  if not limit:
      limit = '300'
  if not (from_value and to):
    resp.say("Invalid request")
    return str(resp)
  from_client = caller.startswith('client')
  # caller_id = os.environ.get("CALLER_ID", CALLER_ID)
  if to.startswith("client:"):
    # client -> client
    resp.dial(callerId=from_value).client(to[7:])
  elif to.startswith("number:"):
    if bcoinUserId:
      callback_url = 'http://api.bcoinpro.website/twilio/events?username=' + bcoinUserId
      resp.dial(callerId=caller_value, timeLimit=limit, action=callback_url, method='POST').number(to[7:])
    else: 
      resp.dial(callerId=caller_value, timeLimit=limit).number(to[7:])
  else:
    resp.say("Invalid request")
  return str(resp)

@app.route('/callDetail1', methods=['GET', 'POST'])
def callDetail1():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  call_sid = request.values.get('call_sid')
  call = client.calls.get(call_sid).fetch()
  if (call.direction != 'inbound'):
    tmp = {'from':call.from_formatted, 'to':call.to_formatted, 'status':call.status, 'duration':call.duration, 'starttime':str(call.start_time)}
    return json.dumps(tmp)
  else:
    for callChild in client.calls.list(parent_call_sid=call.sid):
      if call.from_formatted != '':
        from_f = call.from_formatted
      else: 
        from_f = callChild.from_formatted
      if call.to_formatted != '':
        to_f = call.to_formatted
      else:
        to_f = callChild.to_formatted
      tmp = {'from':from_f, 'to':to_f, 'status':callChild.status, 'duration':callChild.duration, 'starttime':str(callChild.start_time)}
      return json.dumps(tmp)
    
@app.route('/callDetail', methods=['GET', 'POST'])
def callDetail():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  call_sid = request.values.get('call_sid')
  call = client.calls.get(call_sid).fetch()
  if (call.direction != 'inbound'):
    tmp = {'from':call.from_formatted, 'to':call.to_formatted, 'status':call.status, 'duration':call.duration, 'starttime':str(call.start_time), 'isphone':(call.to.startswith('client') == False)}
    return json.dumps(tmp)
  else:
    for callChild in client.calls.list(parent_call_sid=call.sid):
      if call.from_formatted != '':
        from_f = call.from_formatted
      else: 
        from_f = callChild.from_formatted
      if call.to_formatted != '':
        to_f = call.to_formatted
      else:
        to_f = callChild.to_formatted
      tmp = {'from':from_f, 'to':to_f, 'status':callChild.status, 'duration':callChild.duration, 'starttime':str(callChild.start_time), 'isphone':(callChild.to.startswith('client') == False)}
      return json.dumps(tmp)

@app.route('/callLog', methods=['GET', 'POST'])
def callLog():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  client_name = request.values.get('client')
  result = []
  for call in client.calls.list(to="client:"+client_name):
    if call.direction != "inbound":
      tmp = {'contact':call.from_formatted, 'type':'Inbox', 'status':call.status, 'duration':call.duration, 'starttime':str(call.start_time)}
      result.append(tmp)
  for call in client.calls.list(from_="client:"+client_name):
    if call.direction != "inbound":
      tmp = {'type':'Outbox', 'contact':call.to_formatted, 'status':call.status, 'duration':call.duration, 'starttime':str(call.start_time)}
      result.append(tmp)
  k = {'Call': result}
  return json.dumps(k)

@app.route('/outGoingLog', methods=['GET', 'POST'])
def outGoingLog():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  client_name = request.values.get('client')
  result = []
  for call in client.calls.list(from_="client:"+client_name):
    if call.direction == "inbound":
      for childCall in client.calls.list(parent_call_sid=call.sid, from_="(832) 786-5260"):
        tmp = {'type':'Outbox', 'contact':childCall.to_formatted, 'status':childCall.status, 'duration':childCall.duration, 'starttime':str(childCall.start_time)}
        result.append(tmp)
  k = {'Call': result}
  return json.dumps(k)

@app.route('/contactList', methods=['GET', 'POST'])
def contactList():
  return json.dumps({'contact': CONTACT_LIST})

@app.route('/', methods=['GET', 'POST'])
def welcome():
  resp = twilio.twiml.Response()
  resp.say("Welcome to Twilio")
  return str(resp)

@app.route('/countDuration', methods=['GET', 'POST'])
def countDuration():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  client_name = request.values.get('client')
  now = date.today()
  result = []
  for call in client.calls.list(to="client:"+client_name, status="completed", start_time=date(2017, 1, 3)):
    if call.direction != "inbound":
      tmp = {'type':'Inbox', 'contact':call.to_formatted, 'status':call.status, 'duration':call.duration, 'starttime':str(call.start_time)}
      result.append(tmp)
  k = {'Call': result}
  return json.dumps(k)

@app.route('/sendSms', methods=['GET', 'POST'])
def sendSms():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)
  client = Client(api_key, api_key_secret, account_sid)
  
  from_value = request.values.get('From')
  to_value = request.values.get('To')
  body_sms = request.values.get('Body')
  
  message = client.messages.create(to=to_value, from_=from_value, body=body_sms)
  k = {'message': str(message)}
  return json.dumps(k)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=False)
