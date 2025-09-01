"""
Utilitário para validação de emails institucionais do Inteli.
"""

def is_valid_inteli_email(email: str) -> bool:
    """
    Valida se o email é um email institucional válido do Inteli.
    
    Args:
        email: Email a ser validado
        
    Returns:
        True se o email for válido, False caso contrário
    """
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip().lower()
    
    # Lista de domínios permitidos
    allowed_domains = [
        "@sou.inteli.edu.br",    # Alunos
        "@prof.inteli.edu.br"    # Professores
    ]
    
    return any(email.endswith(domain) for domain in allowed_domains)

def get_email_domain_type(email: str) -> str:
    """
    Retorna o tipo de domínio do email.
    
    Args:
        email: Email a ser analisado
        
    Returns:
        "aluno" para @sou.inteli.edu.br, "professor" para @prof.inteli.edu.br, "invalid" para outros
    """
    if not email or not isinstance(email, str):
        return "invalid"
    
    email = email.strip().lower()
    
    if email.endswith("@sou.inteli.edu.br"):
        return "aluno"
    elif email.endswith("@prof.inteli.edu.br"):
        return "professor"
    else:
        return "invalid"

def get_allowed_domains_text() -> str:
    """
    Retorna texto com os domínios permitidos para exibição.
    
    Returns:
        String com os domínios permitidos
    """
    return "@sou.inteli.edu.br ou @prof.inteli.edu.br"

def get_placeholder_text() -> str:
    """
    Retorna texto de placeholder para campos de email.
    
    Returns:
        String com exemplo de email
    """
    return "seu.nome@sou.inteli.edu.br"
