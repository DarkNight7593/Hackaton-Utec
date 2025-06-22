# generar_diagrama.py (Lambda principal)
import boto3, os, uuid, json
from datetime import datetime

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')
BUCKET = os.environ["BUCKET_DIAGRAMAS"]
FUNCION_VALIDAR = os.environ["FUNCION_VALIDAR"]
FUNCION_AWS = os.environ["FUNCION_DIAGRAMA_AWS"]
FUNCION_ER = os.environ["FUNCION_DIAGRAMA_ER"]
FUNCION_JSON = os.environ["FUNCION_DIAGRAMA_JSON"]

def lambda_handler(event, context):
    try:
        token = event['headers'].get('Authorization')
        if not token:
            return {'statusCode': 403, 'body': 'Token no proporcionado'}

        validar = lambda_client.invoke(
            FunctionName=FUNCION_VALIDAR,
            InvocationType='RequestResponse',
            Payload=json.dumps({ 'token': token })
        )
        payload = json.loads(validar['Payload'].read())
        if payload['statusCode'] != 200:
            return {'statusCode': 403, 'body': 'Token inválido'}

        tenant_id = payload['body']['tenant_id']
        data = json.loads(event['body'])
        codigo = data.get('codigo')
        tipo = data.get('tipo')

        if not codigo or not tipo:
            return {'statusCode': 400, 'body': 'Faltan campos obligatorios'}

        diagrama_id = str(uuid.uuid4())
        nombre_img = f"{tenant_id}/{diagrama_id}/imagen.png"
        nombre_src = f"{tenant_id}/{diagrama_id}/source.txt"

        funcion_objetivo = {
            "aws": FUNCION_AWS,
            "er": FUNCION_ER,
            "json": FUNCION_JSON
        }.get(tipo)

        if not funcion_objetivo:
            return {'statusCode': 400, 'body': 'Tipo de diagrama no válido'}

        render_result = lambda_client.invoke(
            FunctionName=funcion_objetivo,
            InvocationType='RequestResponse',
            Payload=json.dumps({ 'codigo': codigo })
        )
        resultado = json.loads(render_result['Payload'].read())

        if resultado.get('statusCode') != 200:
            return {'statusCode': 500, 'body': resultado.get('body')}

        image_bytes = bytes(resultado['body']['image'], encoding='latin1')

        s3.put_object(Bucket=BUCKET, Key=nombre_src, Body=codigo.encode('utf-8'), ContentType='text/plain')
        s3.put_object(Bucket=BUCKET, Key=nombre_img, Body=image_bytes, ContentType='image/png', ACL='public-read')

        url_publica = f"https://{BUCKET}.s3.amazonaws.com/{nombre_img}"

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Diagrama generado',
                'url': url_publica,
                'diagrama_id': diagrama_id
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}