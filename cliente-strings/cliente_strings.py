import socket
from datetime import datetime


class ClienteStrings:
    
    def __init__(self, host: str, port: int = 8080, timeout: int = 30):
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
    
    def enviar(self, mensagem):
        """Envia mensagem ao servidor"""
        if not mensagem.endswith('\n'):
            mensagem += '\n'
        self.socket.sendall(mensagem.encode('utf-8'))
        print(f"\n{'─'*60}")
        print(f"📤 ENVIANDO:")
        print(f"{mensagem.strip()}")
        print('─'*60)
    
    def receber(self):
        """Recebe resposta do servidor"""
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
        
        resposta = dados.decode('utf-8').strip()
        return resposta
    
    def parsear(self, resposta):
        """Faz parsing da resposta e exibe formatado"""
        if resposta.endswith('|FIM'):
            resposta = resposta[:-4]
        
        resultado = {}
        partes = resposta.split('|')
        
        if partes:
            resultado['tipo'] = partes[0]
        
        for parte in partes[1:]:
            if '=' in parte:
                chave, valor = parte.split('=', 1)
                resultado[chave] = valor

        """print(f"\n{'─'*60}")
        print(f"📥 RESPOSTA:")
        print(f"Tipo: {resultado.get('tipo', 'N/A')}")
        
        if resultado.get('tipo') == 'OK':
            for chave, valor in resultado.items():
                if chave != 'tipo' and len(valor) < 100:
                    print(f"{chave}: {valor}")
        elif resultado.get('tipo') == 'ERROR':
            print(f"Erro: {resultado.get('msg', 'Erro desconhecido')}")
        
        print('─'*60)"""
        
        return resultado
    
    def autenticar(self, aluno_id):
        """Autentica no servidor"""
        timestamp = datetime.now().isoformat()
        mensagem = f"AUTH|aluno_id={aluno_id}|timestamp={timestamp}|FIM"
        
        self.enviar(mensagem)
        resposta = self.receber()
        dados = self.parsear(resposta)
        
        if dados.get('tipo') == 'OK':
            self.token = dados.get('token')
            print(f"\nAutenticado como {dados.get('nome')}")
            return True
        print(f"✗ Erro: {dados.get('msg', 'Erro desconhecido')}")
        return False
    
    def operacao(self, nome, **params):
        """Executa uma operação genérica"""
        if not self.token:
            print("Não autenticado")
            return None
        
        msg = f"OP|token={self.token}|operacao={nome}"
        for k, v in params.items():
            msg += f"|{k}={v}"
        msg += "|FIM"
        
        self.enviar(msg)
        resposta = self.receber()
        dados = self.parsear(resposta)
        
        if dados.get('tipo') == 'OK':
            return dados
        print(f"Erro: {dados.get('msg', 'Erro desconhecido')}")
        return None
    
    def echo(self, mensagem):
        """Operação ECHO"""
        return self.operacao("echo", mensagem=mensagem)
    
    def soma(self, numeros):
        """Operação SOMA"""
        # Tenta formato de lista Python
        numeros_str = str(numeros)
        return self.operacao("soma", nums=numeros_str)
    
    def timestamp(self):
        """Operação TIMESTAMP"""
        return self.operacao("timestamp")
    
    def status(self, detalhado=False):
        """Operação STATUS"""
        if detalhado:
            return self.operacao("status", detalhado="true")
        return self.operacao("status")
    
    def historico(self, limite=10):
        """Operação HISTÓRICO"""
        return self.operacao("historico", limite=str(limite))
    
    def logout(self):
        """Encerra sessão"""
        if not self.token:
            return False
        
        msg = f"LOGOUT|token={self.token}|FIM"
        self.enviar(msg)
        resposta = self.receber()
        dados = self.parsear(resposta)
        
        if dados.get('tipo') == 'OK':
            print("Logout realizado")
            self.token = None
            return True
        return False


def main():
    """Função principal"""
    print("="*50)
    print("CLIENTE PROTOCOLO STRINGS")
    print("="*50)
    
    host = "3.88.99.255"
    aluno_id = input("Matrícula: ").strip()
    
    cliente = ClienteStrings(host)
    
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
                if resultado and resultado.get('tipo') == 'OK':
                    print(f"\nEcho: {resultado.get('mensagem_eco')}")
                    print(f"Hash MD5: {resultado.get('hash_md5')}")
                    
            elif opcao == "2":
                nums = input("Números (separados por vírgula): ")
                resultado = cliente.soma(nums)
                if resultado and resultado.get('tipo') == 'OK':
                    print(f"\nSoma: {resultado.get('soma')}")
                    print(f"Média: {resultado.get('media')}")
                    print(f"Máximo: {resultado.get('maximo')}")
                    print(f"Mínimo: {resultado.get('minimo')}")
                    
            elif opcao == "3":
                resultado = cliente.timestamp()
                if resultado and resultado.get('tipo') == 'OK':
                    print(f"\nTimestamp: {resultado.get('timestamp_formatado')}")
                    print(f"Unix: {resultado.get('timestamp_unix')}")
                    print(f"Timezone: {resultado.get('timezone')}")
                    
            elif opcao == "4":
                det = input("Detalhado? (s/n): ").strip().lower() == 's'
                resultado = cliente.status(detalhado=det)
                if resultado and resultado.get('tipo') == 'OK':
                    print(f"\nStatus: {resultado.get('status')}")
                    print(f"Operações: {resultado.get('operacoes_processadas')}")
                    print(f"Tempo ativo: {resultado.get('tempo_ativo')}")
                    if det:
                        print(f"Sessões ativas: {resultado.get('sessoes_ativas')}")
                        print(f"Versão: {resultado.get('versao')}")
                        
                        # Extrai nomes dos alunos ativos
                        sessoes = resultado.get('sessoes_detalhes', '')
                        if sessoes and '{' in sessoes:
                            import ast
                            try:
                                sessoes_dict = ast.literal_eval(sessoes)
                                print(f"\nAlunos ativos:")
                                for matricula, dados in sessoes_dict.items():
                                    nome = dados.get('nome', 'N/A')
                                    ip = dados.get('ip_cliente', 'N/A')
                                    print(f"    • {nome} (Mat: {matricula})")
                            except:
                                pass
                    
            elif opcao == "5":
                resultado = cliente.historico()
                if resultado and resultado.get('tipo') == 'OK':
                    print("\nHISTÓRICO DE OPERAÇÕES")
                    print("─" * 60)
                    print(f"Aluno ID: {resultado.get('aluno_id', 'N/A')}")
                    print(f"Limite solicitado: {resultado.get('limite_solicitado', 'N/A')}")
                    print(f"Total encontrado: {resultado.get('total_encontrado', 'N/A')}")
                    print(f"Timestamp da consulta: {resultado.get('timestamp_consulta', 'N/A')}")
                    print("─" * 60)
                    
                    # Estatísticas gerais
                    estat = resultado.get('estatisticas')
                    if estat:
                        try:
                            import ast
                            estat = ast.literal_eval(estat)
                            print("Estatísticas:")
                            print(f"Total de operações: {estat.get('total_operacoes', 'N/A')}")
                            print(f"Sucesso: {estat.get('operacoes_sucesso', 'N/A')}")
                            print(f"Erros: {estat.get('operacoes_erro', 'N/A')}")
                            print(f"Taxa de sucesso: {estat.get('taxa_sucesso', 'N/A')}%")
                        except Exception:
                            print("Estatísticas: (formato inválido)")
                    
                    print("─" * 60)
                    print(f"Timestamp servidor: {resultado.get('timestamp', 'N/A')}")
                    print("Consulta concluída com sucesso.\n")
                    
            elif opcao == "6":
                cliente.logout()
                break
                
            elif opcao == "0":
                if cliente.token:
                    cliente.logout()
                break
    
    except KeyboardInterrupt:
        print("\nCancelado")
    finally:
        cliente.desconectar()


if __name__ == "__main__":
    main()