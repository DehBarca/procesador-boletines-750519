from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import boto3
import uvicorn
from templates import BOLETIN_TEMPLATE

app = FastAPI(title="Practica 4 - Mostrador Boletines")

# Configurar cliente DynamoDB
dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
TABLE_NAME = "boletines"


def generar_html_boletin(boletin):
    """
    Genera el HTML para mostrar un boletín usando el template.
    """
    html_content = BOLETIN_TEMPLATE.format(
        id=boletin['id'],
        contenido=boletin['contenido'],
        correo_electronico=boletin['correo_electronico'],
        imagen_url=boletin['imagen_url'],
        nombre_archivo=boletin['nombre_archivo'],
        fecha_creacion=boletin['fecha_creacion']
    )
    
    return html_content


@app.get("/boletines/{boletin_id}", response_class=HTMLResponse)
def obtener_boletin(boletin_id: str, correoElectronico: str):
    """
    Obtiene y muestra el contenido de un boletín específico desde DynamoDB.
    """
    try:
        table = dynamodb_resource.Table(TABLE_NAME)
        
        # Buscar el boletín en DynamoDB
        response = table.get_item(Key={'id': boletin_id})
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Boletín no encontrado")
        
        boletin = response['Item']
        
        # Verificar que el email coincida
        if boletin.get('correo_electronico') != correoElectronico:
            raise HTTPException(status_code=404, detail="Boletín no encontrado")
        
        # Marcar el boletín como leído
        table.update_item(
            Key={'id': boletin_id},
            UpdateExpression='SET leido = :val',
            ExpressionAttributeValues={':val': 1}
        )
        
        # Generar HTML usando el template
        html_content = generar_html_boletin(boletin)
        return html_content
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el boletín: {str(e)}")


@app.get("/ping")
def ping():
    """Endpoint para verificar que el servicio está activo"""
    return {"status": "ok", "servicio": "mostrador-boletines"}


if __name__ == "__main__":
    print("Servicio mostrador listo")
    print("Iniciando servidor en puerto 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
