"""
Testes unitários para o modelo de avaliação.
Demonstra boas práticas de testes e cobertura de código.
"""

import unittest
import tempfile
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from src.models.avaliacao import AvaliacaoModel, Avaliacao


class TestAvaliacaoModel(unittest.TestCase):
    """Testes para a classe AvaliacaoModel"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.model = AvaliacaoModel(diretorio_dados=self.temp_dir)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_criar_diretorio_se_nao_existe(self):
        """Testa que o modelo pode ser criado sem criar diretório automaticamente"""
        novo_dir = os.path.join(self.temp_dir, "novo_diretorio")
        model = AvaliacaoModel(diretorio_dados=novo_dir)
        
        # Com a mudança para Supabase, não criamos mais diretórios automaticamente
        self.assertFalse(os.path.exists(novo_dir))
        
        # Mas o método manual ainda deve funcionar para testes
        model._criar_diretorio_se_nao_existe()
        self.assertTrue(os.path.exists(novo_dir))
    
    def test_validar_soma_notas_por_eixo(self):
        """Testa validação da soma de notas por eixo"""
        avaliacoes = {
            1: {'notas': [1, 2, 1], 'feedbacks': ['ok', 'bom', 'regular']},
            2: {'notas': [1, 1, 1], 'feedbacks': ['ok', 'ok', 'ok']},
            3: {'notas': [1, 0, 1], 'feedbacks': ['ok', 'fraco', 'ok']}
        }
        ids_alunos = [1, 2, 3]
        nomes_eixos = ['Eixo1', 'Eixo2', 'Eixo3']
        
        resultado = self.model.validar_soma_notas_por_eixo(avaliacoes, ids_alunos, nomes_eixos)
        
        # Verifica se retorna um dicionário com validação por eixo
        self.assertIsInstance(resultado, dict)
        self.assertIn('Eixo1', resultado)
        self.assertIn('valido', resultado['Eixo1'])
        self.assertIn('soma_atual', resultado['Eixo1'])
        self.assertIn('soma_esperada', resultado['Eixo1'])
    
    def test_validar_notas_individuais(self):
        """Testa validação de notas individuais"""
        avaliacoes = {
            1: {'notas': [1, 2, 0], 'feedbacks': ['ok', 'bom', 'fraco']},
            2: {'notas': [2, 1, 0], 'feedbacks': ['bom', 'ok', 'fraco']}
        }
        ids_alunos = [1, 2]
        nomes_eixos = ['Eixo1', 'Eixo2', 'Eixo3']
        
        resultado = self.model.validar_notas_individuais(avaliacoes, ids_alunos, nomes_eixos, 3, 2)
        
        # Deve retornar True ou False
        self.assertIsInstance(resultado, bool)
    
    def test_calcular_nota_maxima_regra_hibrida(self):
        """Testa cálculo de nota máxima com a regra híbrida"""
        from src.models.usuario import UsuarioModel
        usuario_model = UsuarioModel()
        
        # Testar diferentes tamanhos de grupo com regra híbrida
        casos_teste = [
            (2, 2, "N/2+1"),  # Grupo de 2: N/2+1 = 1+1 = 2
            (3, 2, "N/2+1"),  # Grupo de 3: N/2+1 = 1+1 = 2
            (4, 2, "N/2"),    # Grupo de 4: N/2 = 2
            (5, 2, "N/2"),    # Grupo de 5: N/2 = 2
            (6, 3, "N/2"),    # Grupo de 6: N/2 = 3
            (7, 3, "N/2"),    # Grupo de 7: N/2 = 3
            (8, 4, "N/2"),    # Grupo de 8: N/2 = 4
        ]
        
        for num_integrantes, nota_maxima_esperada, regra_usada in casos_teste:
            with self.subTest(num_integrantes=num_integrantes):
                nota_maxima = usuario_model.calcular_nota_maxima(num_integrantes)
                self.assertEqual(nota_maxima, nota_maxima_esperada, 
                               f"Grupo de {num_integrantes} deveria ter nota máxima {nota_maxima_esperada} (usando {regra_usada}), mas obteve {nota_maxima}")
    
    def test_regra_distribuicao_pontos(self):
        """Testa se a regra permite distribuir todos os pontos por eixo"""
        from src.models.usuario import UsuarioModel
        usuario_model = UsuarioModel()
        
        # Testar se a regra permite distribuir N pontos (número de integrantes) por eixo
        for num_integrantes in range(2, 9):
            nota_maxima = usuario_model.calcular_nota_maxima(num_integrantes)
            pontos_totais_por_eixo = num_integrantes
            max_distribuivel = nota_maxima * (num_integrantes - 1)  # N-1 alunos podem receber nota
            
            with self.subTest(num_integrantes=num_integrantes):
                self.assertGreaterEqual(max_distribuivel, pontos_totais_por_eixo,
                                      f"Grupo de {num_integrantes}: máximo distribuível ({max_distribuivel}) deve ser >= pontos totais ({pontos_totais_por_eixo})")
    
    def test_obter_estatisticas_dados_vazios(self):
        """Testa obtenção de estatísticas com dados vazios"""
        df = pd.DataFrame()
        estatisticas = self.model.obter_estatisticas(df)
        
        self.assertEqual(estatisticas['total_avaliacoes'], 0)
        self.assertEqual(estatisticas['alunos_avaliadores'], 0)
        self.assertEqual(estatisticas['times'], 0)
        self.assertEqual(estatisticas['periodo'], 'N/A')
    
    def test_obter_estatisticas_com_dados(self):
        """Testa obtenção de estatísticas com dados"""
        dados = {
            'timestamp': ['20231201_120000', '20231201_120001'],
            'id_avaliador': [1, 2],
            'time': ['Time A', 'Time A'],
            'id_avaliado': [3, 4],
            'eixo': ['Colaboração', 'Responsabilidade'],
            'nota': [2, 3],
            'feedback': ['Bom trabalho', 'Excelente']
        }
        df = pd.DataFrame(dados)
        
        estatisticas = self.model.obter_estatisticas(df)
        
        self.assertEqual(estatisticas['total_avaliacoes'], 2)
        self.assertEqual(estatisticas['alunos_avaliadores'], 2)
        self.assertEqual(estatisticas['times'], 1)
        self.assertIn('20231201', estatisticas['periodo'])
    
    def test_carregar_dados_mock(self):
        """Testa carregamento de dados usando mock do Supabase"""
        # Dados simulados
        dados_simulados = [
            {'id_avaliador': 1, 'nome_avaliador': 'João', 'nota': 3},
            {'id_avaliador': 2, 'nome_avaliador': 'Maria', 'nota': 2}
        ]

        with patch('src.models.avaliacao.download_json_from_bucket') as mock_download, \
             patch('tempfile.NamedTemporaryFile') as mock_temp, \
             patch('pandas.read_json') as mock_read_json, \
             patch('os.unlink') as mock_unlink:

            mock_temp.return_value.__enter__.return_value.name = '/tmp/test.json'
            mock_read_json.return_value = pd.DataFrame(dados_simulados)
            # Simula download sem erro
            mock_download.return_value = None

            # Executar método
            df = self.model.carregar_dados()

            # Verificar que pandas foi chamado e arquivo foi limpo
            mock_read_json.assert_called_once()
            mock_unlink.assert_called_once()

            # Verificar dados retornados
            self.assertEqual(len(df), 2)
            self.assertEqual(df.iloc[0]['nome_avaliador'], 'João')
    
    def test_carregar_dados_erro_retorna_dataframe_vazio(self):
        """Testa que carregar_dados retorna DataFrame vazio em caso de erro"""
        # Mock para simular erro no download
        with patch('src.models.avaliacao.download_json_from_bucket') as mock_download:
            mock_download.side_effect = Exception("Erro Supabase")
            
            # Executar método
            df = self.model.carregar_dados()
            
            # Verificar que retorna DataFrame vazio
            self.assertTrue(df.empty)
            self.assertIsInstance(df, pd.DataFrame)


class TestAvaliacao(unittest.TestCase):
    """Testes para a classe Avaliacao"""
    
    def test_criar_avaliacao(self):
        """Testa criação de uma avaliação"""
        avaliacao = Avaliacao(
            timestamp="20231201_120000",
            id_avaliador=1,
            time="Time A",
            id_avaliado=2,
            eixo="Colaboração",
            nota=3,
            feedback="Excelente trabalho em equipe"
        )
        
        self.assertEqual(avaliacao.timestamp, "20231201_120000")
        self.assertEqual(avaliacao.id_avaliador, 1)
        self.assertEqual(avaliacao.time, "Time A")
        self.assertEqual(avaliacao.id_avaliado, 2)
        self.assertEqual(avaliacao.eixo, "Colaboração")
        self.assertEqual(avaliacao.nota, 3)
        self.assertEqual(avaliacao.feedback, "Excelente trabalho em equipe")


if __name__ == '__main__':
    unittest.main()
