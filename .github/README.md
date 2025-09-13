# 🧙‍♂️ TreeMancer CI/CD Pipeline

Este diretório contém os workflows de integração e entrega contínua para o TreeMancer.

## 📋 Workflows

### 🔧 CI (Continuous Integration) - `ci.yaml`

**Triggers:**
- Push para `main`, `develop`, ou branches `feat/*`
- Pull Requests para `main` ou `develop`

**Jobs:**
1. **Test** - Executa em Python 3.12 e 3.13
   - Format check (ruff)
   - Lint (ruff) 
   - Type check (pyright)
   - Tests com coverage
   - Upload coverage para Codecov

2. **Build** - Constrói o pacote (somente em push para main/develop)
   - Build com uv
   - Armazena artifacts

3. **Integration Test** - Testa a instalação real do pacote
   - Instala o pacote construído
   - Testa comandos CLI básicos

### 🚀 CD (Continuous Deployment) - `cd.yaml`

**Triggers:**
- Release publicado no GitHub
- Dispatch manual com versão especificada

**Jobs:**
1. **Validate** - Validação completa antes do deploy
2. **Build** - Build para múltiplas plataformas 
3. **Integration Test** - Testes em Ubuntu, Windows e macOS
4. **Deploy Test** - Deploy para Test PyPI
5. **Deploy Prod** - Deploy para PyPI (somente releases)
6. **GitHub Release** - Cria release automaticamente (dispatch manual)

### 🔍 Quality (Quality Assurance) - `quality.yaml`

**Triggers:**
- Push para `main` ou `develop`
- Pull Requests
- Schedule semanal (Segundas 2h UTC)

**Jobs:**
1. **Security** - Verificações de segurança
2. **Dependency Review** - Review de dependências (PRs)
3. **Performance** - Benchmarks básicos (main)
4. **Compatibility** - Testes cross-platform
5. **Docs** - Verificação de documentação

## 🔄 Dependabot - `dependabot.yml`

Atualização automática de dependências:
- GitHub Actions (semanal)
- Dependências Python (semanal)
- Agrupamento inteligente por tipo

## 🎯 Melhores Práticas Implementadas

### ✅ Separação de Responsabilidades
- **CI**: Validação rápida para feedback aos desenvolvedores
- **CD**: Deploy seguro e controlado
- **Quality**: Verificações abrangentes e monitoramento

### ✅ Segurança
- Environments protegidos para deploy
- Secrets management
- Dependency review automático
- Security scanning

### ✅ Performance
- Builds condicionais
- Cache de dependências (via uv)
- Matrix builds otimizados
- Artifacts com retenção apropriada

### ✅ Observabilidade
- Coverage tracking
- Performance benchmarks
- Cross-platform testing
- Documentação validation

## 🚦 Fluxo de Deploy

```
Feature Branch → PR → CI → Merge → 
    ↓
Main Branch → Quality Check → 
    ↓
Manual Release/Tag → CD Pipeline →
    ↓
Test PyPI → Production PyPI → GitHub Release
```

## 🛠️ Como Usar

### Para Desenvolvimento
```bash
# Push normal - executa CI
git push origin feat/nova-funcionalidade

# PR - executa CI completo + Quality checks
gh pr create
```

### Para Release
```bash
# Opção 1: GitHub Release (recomendado)
gh release create v1.0.0 --title "TreeMancer v1.0.0" --notes "Release notes"

# Opção 2: Dispatch manual
gh workflow run cd.yaml -f version=v1.0.0
```

## 📊 Status Badges

Adicione ao README principal:

```markdown
[![CI](https://github.com/ericmiguel/treemancer/workflows/CI/badge.svg)](https://github.com/ericmiguel/treemancer/actions/workflows/ci.yaml)
[![CD](https://github.com/ericmiguel/treemancer/workflows/CD/badge.svg)](https://github.com/ericmiguel/treemancer/actions/workflows/cd.yaml)
[![Quality](https://github.com/ericmiguel/treemancer/workflows/Quality/badge.svg)](https://github.com/ericmiguel/treemancer/actions/workflows/quality.yaml)
```