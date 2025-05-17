import requests
from typing import Dict, List, Optional, Union
from langchain.tools import tool


@tool
def list_products(search_query: Optional[str] = None) -> Union[List[Dict], Dict]:
    """
    Lista todos los productos disponibles del catálogo.

    Args:
        search_query (Optional[str]): Filtro de búsqueda para productos (por nombre, categoría, etc.)

    Returns:
        List[Dict]: Lista de productos con sus detalles si la llamada fue exitosa.
        Dict: Un diccionario con clave 'error' si hubo un fallo.
    """
    login_url = "http://127.0.0.1:8000/api/login"
    login_data = {
        "email": "jorge@gmail.com",
        "password": "password",
    }

    try:
        # Realizar login
        login_response = requests.post(login_url, json=login_data)
        login_response.raise_for_status()

        # Extraer token
        token = login_response.json().get('data', {}).get('token')
        if not token:
            return {"error": "No se pudo obtener el token de autenticación."}

        # Configurar headers con el token
        headers = {
            'Authorization': f'Bearer {token}'
        }

        # Construir URL para obtener productos
        products_url = "http://127.0.0.1:8000/api/products"
        if search_query:
            products_url += f"?search={search_query}"

        # Obtener productos
        products_response = requests.get(products_url, headers=headers)
        products_response.raise_for_status()

        data = products_response.json()
        # Aquí suponemos que la API responde con una estructura tipo {"data": [...]}
        products = data.get('data', [])
        
        print(products_response.json())
        return products

    except requests.exceptions.RequestException as e:
        return {"error": f"Error al obtener los productos: {str(e)}"}
    


