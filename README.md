# TriProtocol: Clientes Multi-Protocolo

Implementação de três clientes que se comunicam com servidores remotos usando diferentes protocolos de comunicação para análise comparativa.

**Disciplina:** Sistemas Distribuídos  
**Trabalho Prático:** Análise de Protocolos de Comunicação

---

## Protocolos Implementados

- **Strings** (Porta 8080) - Texto estruturado com separadores
- **JSON** (Porta 8081) - Objetos JSON estruturados
- **Protocol Buffers** (Porta 8082) - Mensagens binárias serializadas

---

## Instalação

### Dependências

```bash
pip install protobuf
```

### Compilar Protocol Buffers

```bash
# Instalar compilador
sudo apt-get install protobuf-compiler  # Ubuntu/Debian
brew install protobuf                   # macOS

# Compilar schema
protoc --python_out=. messages.proto
```

---

## Uso

### Cliente Strings
```bash
python cliente_strings.py
```

### Cliente JSON
```bash
python cliente_json.py
```

### Cliente Protocol Buffers
```bash
python cliente_protobuf.py
```


---

## Operações Disponíveis

Todos os clientes implementam:

1. **AUTH** - Autenticação com matrícula
2. **ECHO** - Retorna mensagem com hash MD5
3. **SOMA** - Calcula estatísticas de números (soma, média, max, min)
4. **TIMESTAMP** - Retorna informações temporais do servidor
5. **STATUS** - Status do servidor (básico ou detalhado)
6. **HISTÓRICO** - Histórico de operações do aluno
7. **LOGOUT** - Encerra sessão

---

## Fluxo de Comunicação

```
1. Conectar ao servidor TCP
2. Autenticar com matrícula
3. Receber token de sessão
4. Executar operações com token
5. Logout
6. Desconectar
```

---

## Comparação de Protocolos

| Característica | Strings | JSON | Protocol Buffers |
|----------------|---------|------|------------------|
| Tamanho | Grande | Médio | Pequeno (-60%) |
| Legibilidade | Alta | Alta | Baixa |
| Parsing | Complexo | Fácil | Fácil |
| Tipagem | Nenhuma | Fraca | Forte |
| Performance | Baixa | Média | Alta |
| Setup | Nenhum | Nenhum | Compilação |

---

## Exemplos de Mensagens

### Strings
```
AUTH|aluno_id=554576|timestamp=2025-11-12T14:22:00|FIM
OK|token=abc123|nome=THIAGO SIQUEIRA|matricula=554576|FIM
```

### JSON
```json
{"tipo": "autenticar", "aluno_id": "554576", "timestamp": "2025-11-12T14:22:00"}
{"sucesso": true, "token": "abc123", "dados_aluno": {"nome": "THIAGO SIQUEIRA"}}
```

### Protocol Buffers
```
[4 bytes tamanho][dados binários serializados]
```

---

## Configuração do Servidor

- **Host:** 3.88.99.255
- **Porta Strings:** 8080
- **Porta JSON:** 8081
- **Porta Protocol Buffers:** 8082
- **Timeout:** 30 segundos
- **Validade do Token:** 1 hora

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Timeout ao conectar | Verificar IP/porta e firewall |
| Token inválido | Token expirou, fazer nova autenticação |
| messages_pb2.py não encontrado | Compilar com `protoc --python_out=. messages.proto` |
| Matrícula não autorizada | Verificar com professor |

---

## Autor

**Nome:** Thiago Siqueira de Sousa  
**Matrícula:** 554576  

---
