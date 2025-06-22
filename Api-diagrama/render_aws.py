# render_aws.py
import tempfile
from io import BytesIO
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

def lambda_handler(event, context):
    try:
        body = event['body']
        codigo = body['codigo']
        if not codigo:
            return {'statusCode': 400, 'body': 'Código no proporcionado'}

        with tempfile.TemporaryDirectory() as tmpdir:
            scope = {
                "__builtins__": __builtins__,
                "Diagram": Diagram,
                "EC2": EC2,
                "RDS": RDS,
                "ELB": ELB
            }
            exec(codigo, scope)
            img_path = f"{tmpdir}/Simple Web Service.png"
            with open(img_path, "rb") as f:
                imagen_bytes = f.read()

        return {'statusCode': 200, 'body': {'image': imagen_bytes.decode('latin1')}}
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
