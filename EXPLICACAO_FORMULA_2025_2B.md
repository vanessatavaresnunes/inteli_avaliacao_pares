# Explicação da Fórmula de Cálculo de Notas - Período 2025-2B

## Fórmula Implementada

Para o período **2025-2B**, a fórmula de cálculo do índice de avaliação é:

```
Índice = 7.5 × (Px - Pmédi) / ((Pmax - Pmin) + K)
```

Com **limite entre -0.4 e +0.4**, ou seja:
```
Índice_final = max(-0.4, min(0.4, Índice_calculado))
```

### Onde:
- **Px** = Pontos totais recebidos pelo aluno individual (soma de todas as avaliações recebidas)
- **Pmédi** = Média dos pontos totais de todos os alunos do grupo
- **Pmax** = Máximo de pontos totais no grupo
- **Pmin** = Mínimo de pontos totais no grupo
- **K** = Valor de lastro (ballast) que varia conforme o tamanho do grupo (N)

### Valores de K por Tamanho de Grupo:

| Tamanho do Grupo (N) | Valor de K |
|----------------------|------------|
| 4 alunos             | 9          |
| 5 alunos             | 14         |
| 6 alunos             | 44         |
| 7 alunos             | 54         |
| 8 alunos             | 99         |

---

## Por Que Esta Fórmula Foi Implementada?

### 1. Contexto da Avaliação 360

O sistema de avaliação de pares funciona como uma **avaliação 360 graus**, onde:
- Cada aluno avalia todos os colegas do seu grupo (exceto a si mesmo)
- Cada aluno também faz uma autoavaliação
- As avaliações são feitas em três eixos: Entregas Reais, Valor Percebido e Caixa de Ferramentas

### 2. Objetivo da Normalização

A fórmula tem como objetivo **normalizar as notas** de forma que:
- Alunos que se destacam positivamente recebam índices positivos
- Alunos que ficam abaixo da média recebam índices negativos
- As diferenças sejam significativas, mas não extremas
- O intervalo final fique entre **-0.4 e +0.4**

### 3. Problema da Fórmula Anterior

A fórmula original usada em períodos anteriores era:
```
Índice = (Px - Pmédi) / (0.6 × Amplitude)
```

**Problemas identificados:**
- Gerava intervalos muito amplos (aproximadamente -1.4 a +1.4)
- As diferenças entre alunos eram muito grandes
- Não havia controle sobre o intervalo máximo

### 4. Evolução da Nova Fórmula

A nova fórmula foi desenvolvida em etapas:

#### Etapa 1: Fórmula Base com K
```
Índice = (Px - Pmédi) / ((Pmax - Pmin) + K)
```

**Justificativa:**
- O valor **K (lastro)** impede que o denominador fique muito pequeno quando há alto consenso no grupo
- Quando há **baixo consenso** (alta amplitude), a fórmula suaviza o impacto
- Quando há **alto consenso** (baixa amplitude), pequenas diferenças se tornam significativas

**Problema identificado:**
- Os índices ficaram muito pequenos (aproximadamente -0.08 a +0.08)
- As distâncias entre alunos eram muito pequenas, não refletindo adequadamente as diferenças de desempenho

#### Etapa 2: Adição do Fator Multiplicador
```
Índice = 7.5 × (Px - Pmédi) / ((Pmax - Pmin) + K)
```

**Justificativa:**
- O fator **7.5** amplifica as diferenças, tornando-as mais significativas
- Mantém a estrutura da fórmula original com K
- Permite melhor distinção entre alunos com desempenhos diferentes

**Resultado:**
- Intervalo aproximado: -0.59 a +0.61
- Amplitude média: 0.60
- Distâncias significativas entre alunos

#### Etapa 3: Adição do Limite
```
Índice_final = max(-0.4, min(0.4, Índice_calculado))
```

**Justificativa:**
- Garante que o intervalo final seja exatamente **-0.4 a +0.4**
- Previne valores extremos que possam distorcer a avaliação
- Mantém a consistência entre diferentes grupos e turmas
- Facilita a interpretação e comparação dos resultados

**Resultado Final:**
- Intervalo garantido: **-0.4 a +0.4**
- Amplitude média: 0.44
- Distâncias significativas mantidas
- Consistência entre grupos

---

## Como a Fórmula Funciona na Prática

### Exemplo: Grupo com 7 alunos (N=7, K=54)

**Dados do grupo:**
- Aluno A: 20 pontos
- Aluno B: 17 pontos
- Aluno C: 17 pontos
- Aluno D: 16 pontos
- Aluno E: 15 pontos (média)
- Aluno F: 10 pontos
- Aluno G: 10 pontos

**Cálculos:**
- Pmédi = 15.00
- Pmax = 20
- Pmin = 10
- Amplitude = 10
- K = 54
- Denominador = 10 + 54 = 64

**Para o Aluno A (Px = 20):**
```
Índice = 7.5 × (20 - 15) / 64
Índice = 7.5 × 5 / 64
Índice = 37.5 / 64
Índice = 0.586
Índice_final = min(0.4, 0.586) = 0.4 ✅
```

**Para o Aluno E (Px = 15, na média):**
```
Índice = 7.5 × (15 - 15) / 64
Índice = 7.5 × 0 / 64
Índice = 0.0 ✅
```

**Para o Aluno F (Px = 10):**
```
Índice = 7.5 × (10 - 15) / 64
Índice = 7.5 × (-5) / 64
Índice = -37.5 / 64
Índice = -0.586
Índice_final = max(-0.4, -0.586) = -0.4 ✅
```

---

## Vantagens da Fórmula Implementada

### 1. **Normalização Relativa ao Grupo**
- Cada grupo é avaliado em relação à sua própria média
- Grupos com diferentes níveis de desempenho são tratados de forma justa
- Alunos que se destacam em seu grupo recebem reconhecimento adequado

### 2. **Consideração do Consenso**
- O valor K ajusta a sensibilidade da fórmula baseado no consenso do grupo
- Grupos com alto consenso: pequenas diferenças são amplificadas
- Grupos com baixo consenso: diferenças são suavizadas

### 3. **Intervalo Controlado**
- Limite de -0.4 a +0.4 garante consistência
- Facilita a interpretação e comparação entre grupos
- Previne valores extremos que possam distorcer a avaliação

### 4. **Distâncias Significativas**
- O fator 7.5 amplifica diferenças de forma adequada
- Mantém distinção clara entre alunos com diferentes desempenhos
- Não suaviza demais (como a fórmula original com K)
- Não amplifica demais (como a fórmula antiga sem K)

### 5. **Adaptação ao Tamanho do Grupo**
- Valores de K diferentes para diferentes tamanhos de grupo
- Garante que a fórmula funcione bem independente do número de alunos
- Considera as características específicas de cada configuração de grupo

---

## Comparação com Outras Abordagens Testadas

Durante o desenvolvimento, foram testadas várias parametrizações:

| Abordagem | Intervalo | Amplitude Média | Status |
|-----------|-----------|-----------------|--------|
| Original (K atual) | -0.08 a +0.08 | 0.08 | ❌ Muito suavizado |
| K reduzido (15%) | -0.28 a +0.34 | 0.32 | ⚠️ Ainda pequeno |
| Fator 5x | -0.39 a +0.41 | 0.40 | ⚠️ Abaixo do objetivo |
| Fator 7x | -0.55 a +0.57 | 0.56 | ✅ Próximo do objetivo |
| **Fator 7.5x com limite 0.4** | **-0.4 a +0.4** | **0.44** | **✅ IMPLEMENTADO** |
| Fator 10x | -0.78 a +0.81 | 0.80 | ❌ Muito amplo |

A opção escolhida (**Fator 7.5x com limite 0.4**) foi selecionada porque:
- Atende exatamente ao objetivo de intervalo -0.4 a +0.4
- Mantém distâncias significativas entre alunos
- Garante consistência entre grupos
- Previne valores extremos

---

## Aplicação no Sistema

A fórmula é aplicada automaticamente quando:
- O período acadêmico configurado é **2025-2B**
- A variável de ambiente `PERIODO_ATUAL` está definida como `"2025-2B"`

Para outros períodos (como 2025-2A), o sistema continua usando a fórmula anterior:
```
Índice = (Total - Média) / (0.6 × Amplitude)
```

Isso garante:
- Compatibilidade com dados históricos
- Flexibilidade para diferentes períodos
- Possibilidade de ajustes futuros sem afetar períodos anteriores

---

## Conclusão

A fórmula implementada representa um equilíbrio entre:
- **Justiça**: Normalização relativa ao grupo
- **Sensibilidade**: Distinção adequada entre desempenhos diferentes
- **Consistência**: Intervalo controlado e previsível
- **Robustez**: Adaptação a diferentes tamanhos de grupo e níveis de consenso

Esta abordagem garante que a avaliação de pares seja justa, significativa e consistente, fornecendo feedback valioso tanto para os alunos quanto para os orientadores.

