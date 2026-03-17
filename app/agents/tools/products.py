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
    login_url = "http://127.0.0.1:8080/api/auth/login"
    login_data = {
        "email": "jorge@gmail.com",
        "password": "password",
    }

    try:
        # Realizar login
        login_response = requests.post(login_url, json=login_data)
        login_response.raise_for_status()

        # Extraer token
        token = login_response.json().get('token')
        if not token:
            return {"error": "No se pudo obtener el token de autenticación."}

        # Configurar headers con el token
        headers = {
            'Authorization': f'Bearer {token}'
        }

        # Construir URL para obtener productos
        products_url = "http://127.0.0.1:8080/api/v1/products"

        # Obtener productos
        products_response = requests.get(products_url, headers=headers)
        products_response.raise_for_status()

        data = products_response.json()
        # La API de spring devuelve {"message": "...", "data": [...]}
        products = data.get('data', [])
        
        # Filtro local en caso de que el backend no lo soporte
        if search_query:
            search_query_lower = search_query.lower()
            products = [
                p for p in products 
                if search_query_lower in str(p.get('name', '')).lower() 
                or search_query_lower in str(p.get('description', '')).lower()
                or search_query_lower in str(p.get('categoryName', '')).lower()
                or search_query_lower in str(p.get('brandName', '')).lower()
            ]
            
        print(f"Retornando {len(products)} productos.")
        return products

    except requests.exceptions.RequestException as e:
        return {"error": f"Error al obtener los productos: {str(e)}"}
    


