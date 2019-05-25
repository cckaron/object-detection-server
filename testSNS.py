import boto3



def clients(message):
    client =boto3.client(
        #服務名稱
        'sns',
        #帳號身分
        aws_access_key_id="ASIASJ4NQL3ZOJHWFZGY",
        aws_secret_access_key="1dFG5oT0LIFR5V6nB2Uzcnpr7r2ZMuuSklNVCVfg",
        aws_session_token='FQoGZXIvYXdzEL7//////////wEaDLnHJ+dOhi9JkR8tRSKEA++eicVw9deNeXvctaervP1VXX74aXmLeaGxjWr8niQjmAtKfhMEtTkkch+K/Kd2K2ms5TzFKYknB2phzpYzRih7nWHBx1hQO5c/zMCgP9tDw0tVrLHbM0NGfwvdHSxGDxtcLqbPzYQ6OtLnoqLJMkUEDwbUlWUD1gVYRDeTQ9iZ4Jge2wZamSFxjwMiMuISrrUE3Xfw/4BBogoYXBAOv6p6LWIehfOB+SD2YNz7qEDQdvtSm9EFuOfn33dnIZwvPbEhrFd9lbTENUtd8XHYsifv9bTWmujShkNaT8SFnReOTpVz2dQ2qOLMpcCBgYLlMaPbJUSHmk4A9zaqGCQXht/F7hwajLtBl9KuhCpn3cjW2zfQRXl2nEg05zpIbkv+HqSIeAIWUIgAP1Emm/9OEsPiQAQao/0mljkSe8LazRYFcB14wW5BedHN7wEhSWEW0oVbhkkjoV+GgB4OzLAV0J8luilbDPIfuVlJijHRQZQno1Fqppx7mwKqB56AhUdqxy88EZwo/ryY5wU=',
        region_name='us-west-2',
        )
   
    client.publish(
                #Topic的編號
        TopicArn='arn:aws:sns:us-west-2:158673690354:mytopic',
        Message = message
        )
    
    
try:
    clients('111')
    print('message was publish')
except:
    print("sns is error")