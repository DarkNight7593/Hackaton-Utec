import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    try:
        # ✅ Leer body como dict (ej. si invocado desde otra Lambda)
        body = event['body']
        token = body['token']
        tenant_id = body['tenant_id']
        
        if not token or not tenant_id:
            return {
                'statusCode': 400,
                'body': {'error': 'Se requieren token y tenant_id'}
            }

        dynamodb = boto3.resource('dynamodb')
        tokens_table = dynamodb.Table(os.environ["TABLE_TOKEN"])
        
        # 🔍 Buscar el token en la tabla
        response = tokens_table.get_item(
            Key={
                'tenant_id': tenant_id,
                'token': token
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': {'error': 'Token no encontrado'}
            }

        # 🧹 Eliminar (invalidar) el token
        tokens_table.delete_item(
            Key={
                'tenant_id': tenant_id,
                'token': token
            }
        )
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Sesión cerrada exitosamente',
                'tenant_id': tenant_id,
                'token_invalidado': token
            }
        }

    except Exception as e:
        print(f"Error en logout: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': f"Error interno: {str(e)}"}
        }
