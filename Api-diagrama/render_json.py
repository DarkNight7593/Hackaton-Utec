import json
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO

def walk_json(g, parent, obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            node = f"{parent}.{k}" if parent else k
            g.add_edge(parent, node) if parent else g.add_node(node)
            walk_json(g, node, v)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            node = f"{parent}[{i}]"
            g.add_edge(parent, node)
            walk_json(g, node, item)
    else:
        leaf = f"{parent}:{obj}"
        g.add_edge(parent, leaf)

def lambda_handler(event, context):
    try:
        body = event['body']
        codigo = body['codigo']

        if not codigo:
            return {'statusCode': 400, 'body': 'Código no proporcionado'}

        data = json.loads(codigo)
        g = nx.DiGraph()
        walk_json(g, None, data)

        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(g, k=0.5, iterations=50)
        nx.draw(g, pos, with_labels=True, node_size=1500, node_color="lightblue", font_size=8)

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches='tight')
        plt.close()
        buffer.seek(0)

        return {
            'statusCode': 200,
            'body': {
                'image': buffer.read().decode('latin1')
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

