# render_er.py
import tempfile
from eralchemy import render_er

def lambda_handler(event, context):
    try:
        codigo = event.get('codigo')
        if not codigo:
            return {'statusCode': 400, 'body': 'Código no proporcionado'}

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = f"{tmpdir}/input.sql"
            output_path = f"{tmpdir}/output.png"

            with open(input_path, "w") as f:
                f.write(codigo)

            render_er(input_path, output_path)

            with open(output_path, "rb") as f:
                imagen_bytes = f.read()

        return {'statusCode': 200, 'body': {'image': imagen_bytes.decode('latin1')}}
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
