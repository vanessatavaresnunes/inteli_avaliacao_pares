-- Configurar políticas de acesso CRUD para o bucket avaliacaopares_2026_1a
-- Execute este SQL no Supabase SQL Editor

-- 1. Política para SELECT (leitura) - qualquer pessoa pode ler
CREATE POLICY "Permitir leitura publica do bucket 2026-1a"
ON storage.objects FOR SELECT
USING (bucket_id = 'avaliacaopares_2026_1a');

-- 2. Política para INSERT (criação) - qualquer pessoa pode criar arquivos
CREATE POLICY "Permitir upload publico do bucket 2026-1a"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'avaliacaopares_2026_1a');

-- 3. Política para UPDATE (atualização) - qualquer pessoa pode atualizar
CREATE POLICY "Permitir atualizacao publica do bucket 2026-1a"
ON storage.objects FOR UPDATE
USING (bucket_id = 'avaliacaopares_2026_1a')
WITH CHECK (bucket_id = 'avaliacaopares_2026_1a');

-- 4. Política para DELETE (remoção) - qualquer pessoa pode remover
CREATE POLICY "Permitir remocao publica do bucket 2026-1a"
ON storage.objects FOR DELETE
USING (bucket_id = 'avaliacaopares_2026_1a');

-- NOTA: Se as políticas já existirem, você verá um erro.
-- Nesse caso, primeiro execute DROP POLICY para remover as antigas,
-- ou use CREATE POLICY IF NOT EXISTS (se disponível).
