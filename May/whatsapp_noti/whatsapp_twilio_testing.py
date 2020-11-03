from twilio.rest import Client 
 
account_sid = 'ACb57b07af4c72e89c16a87a2341d26a32' 
auth_token = '2012586a77273c845da7a014c8aec217' 
client = Client(account_sid, auth_token) 

def send_message():
    message = client.messages.create( 
                                from_='whatsapp:+14155238886',  
                                body='*Testing* every 10 sec from local machine\n😄😄😄',      
                                to='whatsapp:+6596159059' 
                            ) 
    
    print(message.sid)