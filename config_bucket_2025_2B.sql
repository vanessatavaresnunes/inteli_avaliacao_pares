-- Configurar políticas de acesso CRUD para o bucket inteli_avalpares_2025_2B
-- Execute este SQL no Supabase SQL Editor

-- 1. Política para SELECT (leitura) - qualquer pessoa pode ler
CREATE POLICY "Permitir leitura publica do bucket 2025-2B"
ON storage.objects FOR SELECT
USING (bucket_id = 'inteli_avalpares_2025_2B');

-- 2. Política para INSERT (criação) - qualquer pessoa pode criar arquivos
CREATE POLICY "Permitir upload publico do bucket 2025-2B"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'inteli_avalpares_2025_2B');

-- 3. Política para UPDATE (atualização) - qualquer pessoa pode atualizar
CREATE POLICY "Permitir atualizacao publica do bucket 2025-2B"
ON storage.objects FOR UPDATE
USING (bucket_id = 'inteli_avalpares_2025_2B')
WITH CHECK (bucket_id = 'inteli_avalpares_2025_2B');

-- 4. Política para DELETE (remoção) - qualquer pessoa pode remover
CREATE POLICY "Permitir remocao publica do bucket 2025-2B"
ON storage.objects FOR DELETE
USING (bucket_id = 'inteli_avalpares_2025_2B');

-- NOTA: Se as políticas já existirem, você verá um erro.
-- Nesse caso, primeiro execute DROP POLICY para remover as antigas,
-- ou use CREATE POLICY IF NOT EXISTS (se disponível).

