import socket
import struct
from datetime import datetime
import mensagens_pb2 as pb


class ClienteProtobuf:
    
    def __init__(self, host: str, port: int = 8082, timeout: int = 30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.token = None
        
    def conectar(self):
        """Estabelece conexão TCP"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.host, self.port))
        print(f"Conectado a {self.host}:{self.port}")
    
    def desconectar(self):
        """Fecha conexão"""
        if self.socket:
            self.socket.close()
            print("Desconectado")
    
    def enviar(self, requisicao):
        """Envia mensagem Protocol Buffers com cabeçalho de tamanho"""
        dados = requisicao.SerializeToString()
        tamanho = len(dados)
        
        # Envia: 4 bytes (tamanho) + dados
        cabecalho = struct.pack('!I', tamanho)
        self.socket.sendall(cabecalho + dados)
        
        print(f"\n{'─'*60}")
        print("📤 ENVIANDO (Protocol Buffers):")
        print(f"Tamanho: {tamanho} bytes")
        print(requisicao)
        print('─'*60)
    
    def receber(self):
        """Recebe resposta Protocol Buffers com cabeçalho de tamanho"""
        # Lê cabeçalho (4 bytes com tamanho)
        cabecalho = self._receber_exato(4)
        tamanho = struct.unpack('!I', cabecalho)[0]
        
        # Lê dados da mensagem
        dados = self._receber_exato(tamanho)
        
        # Deserializa
        resposta = pb.Resposta()
        resposta.ParseFromString(dados)
        
        print(f"\n{'─'*60}")
        print("📥 RECEBIDO (Protocol Buffers):")
        print(f"Tamanho: {tamanho} bytes")
        print(resposta)
        print('─'*60)
        
        return resposta
    
    def _receber_exato(self, n):
        """Recebe exatamente n bytes"""
        dados = b''
        while len(dados) < n:
            chunk = self.socket.recv(n - len(dados))
            if not chunk:
                raise ConnectionError("Conexão fechada pelo servidor")
            dados += chunk
        return dados
    
    def autenticar(self, aluno_id):
        """Autentica no servidor"""
        requisicao = pb.Requisicao()
        requisicao.auth.aluno_id = aluno_id
        requisicao.auth.timestamp_cliente = datetime.now().isoformat()
        
        self.enviar(requisicao)
        resposta = self.receber()
        
        if resposta.HasField('ok'):
            # Extrai o token do map de dados
            self.token = resposta.ok.dados.get('token', '')
            nome = resposta.ok.dados.get('nome', '')
            matricula = resposta.ok.dados.get('matricula', '')
            
            print(f"\nAUTENTICAÇÃO BEM-SUCEDIDA!")
            print(f"Token: {self.token[:50]}..." if len(self.token) > 50 else f"Token: {self.token}")
            if nome:
                print(f"Nome: {nome}")
            if matricula:
                print(f"Matrícula: {matricula}")
            return True
        elif resposta.HasField('erro'):
            print(f"Erro: {resposta.erro.mensagem}")
            return False
        
        print("Resposta inesperada do servidor")
        return False
    
    def operacao(self, nome, parametros=None):
        """Executa uma operação genérica"""
        if not self.token:
            print("Não autenticado")
            return None
        
        requisicao = pb.Requisicao()
        requisicao.operacao.token = self.token
        requisicao.operacao.operacao = nome
        
        # Adiciona parâmetros ao map
        if parametros:
            for chave, valor in parametros.items():
                requisicao.operacao.parametros[chave] = str(valor)
        
        self.enviar(requisicao)
        resposta = self.receber()
        
        if resposta.HasField('ok'):
            # Converte map de dados para dicionário Python
            resultado = dict(resposta.ok.dados)
            return resultado
        elif resposta.HasField('erro'):
            print(f"✗ Erro: {resposta.erro.mensagem}")
            return None
        
        return None
    
    def echo(self, mensagem):
        """Operação ECHO"""
        return self.operacao("echo", {"mensagem": mensagem})
    
    def soma(self, numeros):
        """Operação SOMA"""
        numeros_str = ','.join(map(str, numeros))
        return self.operacao("soma", {"numeros": numeros_str})
    
    def timestamp(self):
        """Operação TIMESTAMP"""
        return self.operacao("timestamp")
    
    def status(self, detalhado=False):
        """Operação STATUS"""
        params = {"detalhado": "true" if detalhado else "false"}
        return self.operacao("status", params)
    
    def historico(self, limite=10):
        """Operação HISTÓRICO"""
        return self.operacao("historico", {"limite": str(limite)})
    
    def logout(self):
        """Encerra sessão"""
        if not self.token:
            return False
        
        requisicao = pb.Requisicao()
        requisicao.logout.token = self.token
        
        self.enviar(requisicao)
        resposta = self.receber()
        
        if resposta.HasField('ok'):
            print(f"Logout realizado: {resposta.ok.dados.get('mensagem', 'Sucesso')}")
            self.token = None
            return True
        elif resposta.HasField('erro'):
            print(f"Erro: {resposta.erro.mensagem}")
        
        return False


def main():
    """Função principal"""
    print("="*50)
    print("CLIENTE PROTOCOL BUFFERS")
    print("="*50)
    
    host = "3.88.99.255"
    aluno_id = input("Matrícula: ").strip()
    
    cliente = ClienteProtobuf(host)
    
    try:
        cliente.conectar()
        
        if not cliente.autenticar(aluno_id):
            return
        
        # Menu simples
        while True:
            print("\n\033[32m[1. Echo]  [2. Soma]  [3. Timestamp]  [4. Status]  [5. Histórico]  [6. Logout]\033[0m")
            opcao = input("Opção: ").strip()
            
            if opcao == "1":
                msg = input("Mensagem: ")
                resultado = cliente.echo(msg)
                if resultado:
                    print(f"\nResultado:")
                    for k, v in resultado.items():
                        print(f"  {k}: {v}")
                    
            elif opcao == "2":
                nums = input("Números (separados por vírgula): ")
                numeros = [float(n.strip()) for n in nums.split(',')]
                resultado = cliente.soma(numeros)
                if resultado:
                    print(f"\nResultado:")
                    for k, v in resultado.items():
                        print(f"  {k}: {v}")
                    
            elif opcao == "3":
                resultado = cliente.timestamp()
                if resultado:
                    print(f"\nResultado:")
                    for k, v in resultado.items():
                        print(f"  {k}: {v}")
                    
            elif opcao == "4":
                resultado = cliente.status()
                if resultado:
                    print(f"\nResultado:")
                    for k, v in resultado.items():
                        print(f"  {k}: {v}")
                    
            elif opcao == "5":
                resultado = cliente.historico()
                if resultado:
                    print(f"\nResultado:")
                    for k, v in resultado.items():
                        print(f"  {k}: {v}")
                    
            elif opcao == "6":
                cliente.logout()
                break
    
    except KeyboardInterrupt:
        print("\nCancelado")
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cliente.desconectar()


if __name__ == "__main__":
    main()