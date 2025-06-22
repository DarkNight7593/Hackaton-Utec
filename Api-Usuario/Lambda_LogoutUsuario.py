import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    try:
        # Obtener datos del request
        token = event.get('token')
        tenant_id = event.get('tenant_id')
        
        # Validar parámetros requeridos
        if not token or not tenant_id:
            return {
                'statusCode': 400,
                'body': {'error': 'Se requieren token y tenant_id'}
            }

        # Configurar cliente de DynamoDB
        dynamodb = boto3.resource('dynamodb')
        tokens_table = dynamodb.Table(os.environ["TABLE_TOKEN"])
        
        # 1. Verificar si el token existe y pertenece al tenant
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
            
        # 2. Eliminar el token de la tabla (invalidar sesión)
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