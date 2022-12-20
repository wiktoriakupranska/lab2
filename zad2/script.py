import csv, json, os
import pandas as pd
import matplotlib.colors as colors
import boto3

def lambda_handler(event, context):

    master_df = pd.DataFrame()

    for file in os.listdir(os.getcwd()):
        if file.endswith('.csv'):
            master_df = master_df.append(pd.read_csv(file))

    master_df.to_csv('kolory.csv', index=False)

    df = pd.read_csv('kolory.csv')
    hex_value = df['value'].tolist()
    rgb = []
    for i in hex_value:
        new_i = colors.hex2color(i)
        rgb.append(new_i)

    df['rgb'] = rgb 

    df.to_csv('kolory.csv') 

    targetbucket = 'Bucket'
    csvkey = 'kolory.csv'
    jsonkey = 'kolory.json'

    s3 = boto3.resource('s3')
    csv_object = s3.Object(targetbucket, csvkey)
    csv_content = csv_object.get()['Body'].read().splitlines()
    s3_client = boto3.client('s3')
    l=[]

    for line in csv_content:
        x = json.dumps(line.decode('utf-8')).split(',')
        colorname = str(x[1])
        hex = str(x[2])
        rgb = str(x[3])
        y = '{ "Color name": ' + colorname + '"' + ',' + ' "Hex":' + '"' + hex + '"' + ',' + ' "RGB":' + '"' + rgb + '"' + '}'
        l.append(y)

    s3_client.put_object(
        Bucket=targetbucket,
        Body = str(l).replace("'",""),
        Key = jsonkey,
        ServerSideEncryption= 'AES256'
    )