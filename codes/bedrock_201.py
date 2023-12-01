import json
import os
import sys
import boto3
import timeit


# bedrock_client = boto3.client('bedrock')
# bedrock_client.list_foundation_models()

boto3_bedrock = boto3.client(service_name='bedrock-runtime')

prompt = '''Human: 生成10条商品评论，每条20个字左右
\n\nAssistant:
'''



modelId = 'anthropic.claude-v2' 
accept = 'application/json'
contentType = 'application/json'
body = json.dumps({"prompt": prompt,
                 "max_tokens_to_sample":9000,
                 "temperature":0.1,
                 "top_p":0.9,
                  }) 

response = boto3_bedrock.invoke_model_with_response_stream(body=body, modelId=modelId, accept=accept, contentType=contentType)
stream = response.get('body')
output = []
i = 1
if stream:
    for event in stream:
        chunk = event.get('chunk')
        if chunk:
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = chunk_obj['completion']
            output.append(text)
            print(text)
            i+=1