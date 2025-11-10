import socket
import json
from datetime import datetime


class ClienteJSON:
    
    def __init__(self, host: str, port: int = 8081, timeout: int = 30):
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
    
    def enviar(self, dados):
        """Envia JSON ao servidor"""
        mensagem = json.dumps(dados, ensure_ascii=False) + '\n'
        self.socket.sendall(mensagem.encode('utf-8'))
        print(f"\n{'─'*60}")
        print("📤 ENVIANDO:")
        print(json.dumps(dados, indent=2, ensure_ascii=False))
        print('─'*60)
    
    def receber(self):
        """Recebe resposta JSON do servidor"""
        dados = b''
        self.socket.settimeout(2)
        tentativas = 0
        
        while tentativas < 20:
            try:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                dados += chunk
                if b'\n' in dados:
                    break
                tentativas += 1
            except socket.timeout:
                if dados:
                    break
                tentativas += 1
        
        resposta = json.loads(dados.decode('utf-8').strip())
        print(f"\n{'─'*60}")
        print("📥 RECEBIDO:")
        print(json.dumps(resposta, indent=2, ensure_ascii=False))
        print('─'*60)
        return resposta
    
    def autenticar(self, aluno_id):
        """Autentica no servidor"""
        self.enviar({
            "tipo": "autenticar",
            "aluno_id": aluno_id,
            "timestamp": datetime.now().isoformat()
        })
        
        resposta = self.receber()
        if resposta.get('sucesso'):
            self.token = resposta.get('token')
            print(f"\033[32mAutenticado como {resposta['dados_aluno']['nome']}\033[0m")
            return True
        print(f"Erro: {resposta.get('erro')}")
        return False
    
    def operacao(self, nome, parametros=None):
        """Executa uma operação genérica"""
        if not self.token:
            print("\033[31mNão autenticado\033[0m")
            return None
        
        self.enviar({
            "tipo": "operacao",
            "token": self.token,
            "operacao": nome,
            "parametros": parametros or {},
            "timestamp": datetime.now().isoformat()
        })
        
        resposta = self.receber()
        if resposta.get('sucesso'):
            return resposta.get('resultado')
        print(f"Erro: {resposta.get('erro')}")
        return None
    
    def echo(self, mensagem):
        """Operação ECHO"""
        return self.operacao("echo", {"mensagem": mensagem})
    
    def soma(self, numeros):
        """Operação SOMA"""
        return self.operacao("soma", {"numeros": numeros})
    
    def timestamp(self):
        """Operação TIMESTAMP"""
        return self.operacao("timestamp")
    
    def status(self, detalhado=False):
        """Operação STATUS"""
        return self.operacao("status", {"detalhado": detalhado})
    
    def historico(self, limite=10):
        """Operação HISTÓRICO"""
        return self.operacao("historico", {"limite": limite})
    
    def logout(self):
        """Encerra sessão"""
        if not self.token:
            return False
        
        self.enviar({
            "tipo": "logout",
            "token": self.token,
            "timestamp": datetime.now().isoformat()
        })
        
        resposta = self.receber()
        if resposta.get('sucesso'):
            print("Logout realizado")
            self.token = None
            return True
        return False


def main():
    """Função principal"""
    print("="*50)
    print("CLIENTE PROTOCOLO JSON")
    print("="*50)
    host = "3.88.99.255"
    aluno_id = input("Matrícula: ").strip()
    
    cliente = ClienteJSON(host)
    
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
                    print(f"\033[36m{resultado.get('mensagem_eco')}\033[0m")
                    
            elif opcao == "2":
                nums = input("Números (separados por vírgula): ")
                numeros = [float(n.strip()) for n in nums.split(',')]
                resultado = cliente.soma(numeros)
                if resultado:
                    print(f"\033[36mSoma: {resultado.get('soma')}, Média: {resultado.get('media')}\033[0m")
                    
            elif opcao == "3":
                resultado = cliente.timestamp()
                if resultado:
                    print(f"\033[36mTimestamp: {resultado.get('timestamp_formatado')}\033[0m")
                    
            elif opcao == "4":
                resultado = cliente.status()
                if resultado:
                    print(f"\033[36mStatus: {resultado.get('status')}\033[0m")
                    
            elif opcao == "5":
                resultado = cliente.historico()
                if resultado:
                    print(f"\033[36mTotal: {resultado.get('total_encontrado')} operações\033[0m")
                    
            elif opcao == "6":
                cliente.logout()
                break
    
    except KeyboardInterrupt:
        print("\nCancelado")
    finally:
        cliente.desconectar()


if __name__ == "__main__":
    main()