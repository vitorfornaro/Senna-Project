import unicodedata
import re
import logging
from typing import Union, Optional

#Formatar tipos créditos

logger = logging.getLogger(__name__)

def sanitize_numeric(value: Union[str, int, float, None]) -> float:
    """
    Clean and convert values to float, handling formatting issues

    Args:
        value: String, int, or float to convert

    Returns:
        Float value, 0.0 if conversion fails
    """
    if value is None:
        return 0.0
        
    # Si es un valor numérico, devolverlo directamente
    if isinstance(value, (int, float)):
        return float(value)
    
    # Si es una cadena, limpiarla y convertirla
    if isinstance(value, str):
        # Eliminar espacios, saltos de línea y caracteres no imprimibles
        cleaned = value.strip()
        
        # Verificar si la cadena está vacía después de limpiarla
        if not cleaned or cleaned in ['-', 'N/A']:
            return 0.0
            
        try:
            # Limpiar formato de número portugués/europeo (1.234,56 -> 1234.56)
            # 1. Eliminar todos los espacios y caracteres no imprimibles
            cleaned = re.sub(r'\s+', '', cleaned)
            
            # 2. Reemplazar coma por punto para decimales (solo si hay una coma)
            if ',' in cleaned and '.' not in cleaned:
                cleaned = cleaned.replace(',', '.')
            elif ',' in cleaned and '.' in cleaned:
                # Caso europeo (1.234,56)
                cleaned = cleaned.replace('.', '')  # primero eliminar los puntos
                cleaned = cleaned.replace(',', '.')  # luego reemplazar coma por punto
            
            # 3. Eliminar símbolos de moneda
            cleaned = re.sub(r'[€$£¥]', '', cleaned)
            
            return float(cleaned)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to sanitize numeric value '{value}': {str(e)}")
            return 0.0
    
    # Si no es ni número ni cadena, devolver 0
    logger.warning(f"Unexpected type for numeric value: {type(value)}")
    return 0.0

def sanitize_integer(value) -> int:
    """
    Clean and convert values to integer

    Args:
        value: Any value to convert to integer

    Returns:
        Integer value, 0 if conversion fails
    """
    if not value or (isinstance(value, str) and value.strip() in ['-', '', 'N/A']):
        return 0

    try:
        # Si es una cadena, primero limpiarla
        if isinstance(value, str):
            # Eliminar espacios, saltos de línea y caracteres no imprimibles
            value = value.strip()
            
            # Si después de limpiar está vacía, devolver 0
            if not value:
                return 0
        
        # First convert to float to handle decimals, then to int
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        logger.warning(f"Failed to sanitize integer value '{value}'")
        return 0

def clean_text(text: str) -> str:
    """
    Clean text by removing excess whitespace and normalizing line breaks

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""
        
    # Normalize line breaks
    text = re.sub(r'\r\n', '\n', text)
    
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Remove spaces at the beginning of lines
    text = re.sub(r'\n ', '\n', text)
    
    # Remove multiple line breaks
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()

def slugify_product_name(product_name):
    """
    Convierte un nombre de producto financiero a formato slug
    con guiones bajos entre palabras
    """
    
    if product_name is None or product_name == "":
        return ""
    
    normalized = unicodedata.normalize('NFKD', product_name.lower())
    normalized = ''.join([c for c in normalized if not unicodedata.combining(c)])
    slug = re.sub(r'[^\w\s]', '', normalized)
    # Reemplazar espacios con guiones bajos en lugar de eliminarlos
    slug = re.sub(r'\s+', '', slug)
    
    return slug

def map_financial_product(product_name):
    """
    Mapea un producto financiero a su categoría estandarizada

    Args:
        product_name (str): El nombre del producto financiero

    Returns:
        str: La categoría estandarizada
    """
    # Mapa de slugs de productos a categorías estandarizadas
    map_produtos = {
        "creditorenovavellinhadecredito": "Empréstimo bancário",
        "cartaodecreditosemperiododefreefloat": "Cartão de crédito",
        "creditoautomovelexcluindolocacoesfinanceiras": "Empréstimo bancário",
        "creditopessoal": "Empréstimo bancário",
        "cartaodecreditocomperiododefreefloat": "Cartão de crédito",
        "ultrapassagensdecredito": "Cartão de crédito",
        "cartaodecredito": "Cartão de crédito",
        "locacaofinanceiramobiliaria": "Empréstimo bancário",
        "creditoconexo": "Empréstimo bancário",
        "outroscreditos": "Empréstimo bancário",
        "cartaodecreditocartaodedebitodiferido": "Cartão de crédito",
        "creditonaorenovavel": "Empréstimo bancário",
        "creditorenovavelcontacorrentebancaria": "Empréstimo bancário",
        "facilidadesdedescoberto": "Empréstimo bancário",
        "financiamentoaatividadeempresarial": "Empréstimo bancário",
        "locacaofinanceiraimobiliaria": "Empréstimo bancário",
        "outrosavalesegarantiasbancariasprestadas": "Empréstimo bancário",
        "descontoeoutroscreditostituladosporefeitos": "Empréstimo bancário",
        "factoring": "Empréstimo bancário",
        "creditoahabitacao": "Empréstimo bancário",
        "facilidadesdedescobertocomdomiciliacaodeordenadoe": "Empréstimo bancário",
    }

    # Convertir el nombre del producto a slug
    slug = slugify_product_name(product_name)

    # Buscar en el mapa o devolver un valor predeterminado
    return map_produtos.get(slug)