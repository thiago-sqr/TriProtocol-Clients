#!/usr/bin/env python3
"""
Script de exemplo: Cliente Protocolo JSON
Demonstra uso básico de todas as operações
"""

from cliente_json import ClienteJSON

def main():
    # Configuração
    HOST = "3.88.99.255"
    MATRICULA = "554576"  # Substitua pela sua matrícula
    
    # Criar cliente
    cliente = ClienteJSON(HOST, port=8081)
    
    try:
        # Conectar
        print("=" * 60)
        print("EXEMPLO: Cliente Protocolo JSON")
        print("=" * 60)
        cliente.conectar()
        
        # Autenticar
        print("\n1. AUTENTICAÇÃO")
        if not cliente.autenticar(MATRICULA):
            print("Erro na autenticação. Verifique sua matrícula.")
            return
        
        # Echo
        print("\n2. OPERAÇÃO ECHO")
        resultado = cliente.echo("Teste JSON")
        if resultado:
            print(f"Sucesso! Echo: {resultado.get('mensagem_eco')}")
            print(f"Hash MD5: {resultado.get('hash_md5')}")
        
        # Soma
        print("\n3. OPERAÇÃO SOMA")
        numeros = [15.5, 25.3, 30.7, 45.2]
        resultado = cliente.soma(numeros)
        if resultado:
            print(f"Números: {numeros}")
            print(f"Soma: {resultado.get('soma')}")
            print(f"Média: {resultado.get('media')}")
            print(f"Máximo: {resultado.get('maximo')}")
            print(f"Mínimo: {resultado.get('minimo')}")
        
        # Timestamp
        print("\n4. OPERAÇÃO TIMESTAMP")
        resultado = cliente.timestamp()
        if resultado:
            print(f"Timestamp formatado: {resultado.get('timestamp_formatado')}")
            print(f"Timestamp Unix: {resultado.get('timestamp_unix')}")
        
        # Status
        print("\n5. OPERAÇÃO STATUS")
        resultado = cliente.status(detalhado=True)
        if resultado:
            print(f"Status: {resultado.get('status')}")
            print(f"Versão: {resultado.get('versao')}")
        
        # Histórico
        print("\n6. OPERAÇÃO HISTÓRICO")
        resultado = cliente.historico(limite=3)
        if resultado:
            print(f"Total: {resultado.get('total_encontrado')} operações")
        
        # Logout
        print("\n7. LOGOUT")
        cliente.logout()
        
        print("\n" + "=" * 60)
        print("TESTE COMPLETO FINALIZADO COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nErro durante execução: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        cliente.desconectar()


if __name__ == "__main__":
    main()