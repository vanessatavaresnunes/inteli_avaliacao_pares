"""
Configuração global para testes.
Garante que nenhum teste faça conexões reais com Supabase.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# Mock das variáveis de ambiente do Supabase para testes
os.environ.setdefault('NEXT_PUBLIC_SUPABASE_URL', 'https://mock-supabase.com')
os.environ.setdefault('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY', 'mock-key')
os.environ.setdefault('BUCKET_NAME', 'mock-bucket')

# Mock global do cliente Supabase
@pytest.fixture(autouse=True)
def mock_supabase_client():
    """Mock automático do cliente Supabase para todos os testes"""
    with patch('src.utils.supabase_storage.get_supabase_client') as mock_client_factory:
        # Configurar mock para retornar cliente mockado
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_storage.from_().upload.return_value = None
        mock_storage.from_().download.return_value = b'{"mock": "data"}'
        mock_storage.from_().list.return_value = []
        mock_storage.from_().remove.return_value = None
        
        mock_client.storage = mock_storage
        mock_client_factory.return_value = mock_client
        yield mock_client

# Mock global das funções utilitárias do Supabase
@pytest.fixture(autouse=True) 
def mock_supabase_utils():
    """Mock automático das funções utilitárias do Supabase"""
    with patch('src.utils.supabase_storage.upload_json_to_bucket') as mock_upload, \
         patch('src.utils.supabase_storage.download_json_from_bucket') as mock_download, \
         patch('src.utils.supabase_storage.list_json_files_in_bucket') as mock_list:
        
        mock_upload.return_value = None
        mock_download.return_value = None
        mock_list.return_value = []
        
        yield {
            'upload': mock_upload,
            'download': mock_download,
            'list': mock_list
        }