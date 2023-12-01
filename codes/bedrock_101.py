import boto3
import json

bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1', aws_access_key_id='ACCESS_KEY',
    aws_secret_access_key='SECRET_KEY')


def main():
    input = '''
        \n\nHuman: who are you
        \n\nAssistant:
    '''
    print('input is %s' % input)
    body = json.dumps({"prompt": input, "max_tokens_to_sample": 800, "temperature": 1, "top_p": 0.99, "top_k": 250})
    #https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids-arns.html
    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock_client.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

    response_body = json.loads(response.get('body').read())

    print('response_body is %s' % response_body.get('completion'))



if __name__ == '__main__':
    main()
