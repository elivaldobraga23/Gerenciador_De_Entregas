import os
import json
import pywhatkit

# Função para criar os arquivos de entregas
def criar_arquivo(diretorio, nome_arquivo, nome_acumulado):
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

    caminho_arquivo = os.path.join(diretorio, nome_arquivo)
    caminho_acumulado = os.path.join(diretorio, nome_acumulado)

    if not os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'w') as arquivo:
            arquivo.write(f"{'Entregador':<15}\t{'Dia da Entrega':<15}\t   {'Total de Entregas':<15}\t {'Valor Total (R$)':<15}\n")
        print(f"Arquivo '{caminho_arquivo}' criado com sucesso.")
    else:
        print(f"Arquivo '{caminho_arquivo}' já existe.")
    
    if not os.path.exists(caminho_acumulado):
        with open(caminho_acumulado, 'w') as acumulado:
            json.dump({"total_geral": 0.0, "total_entregas_geral": 0, "entregadores": {}}, acumulado)
        print(f"Arquivo '{caminho_acumulado}' criado com sucesso.")
    else:
        print(f"Arquivo '{caminho_acumulado}' já existe.")

# Função para visualizar o conteúdo do arquivo de entregas
def ver_arquivo(caminho_arquivo, caminho_acumulado):
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'r') as arquivo:
            print("\n=== Entregas Cadastradas ===")
            linhas = arquivo.readlines()
            print(linhas[0], end="")
            print('-' * 75)

            for linha in linhas[1:]:
                if linha.strip():
                    print(linha, end="")
                    print('-' * 75)

        if os.path.exists(caminho_acumulado):
            with open(caminho_acumulado, 'r') as acumulado:
                valores_acumulados = json.load(acumulado)
                print("\n=== Valores Acumulados por Entregador ===")
                for entregador, dados in valores_acumulados["entregadores"].items():
                    print(f"{entregador:<15} {'Total de Entregas: ' + str(dados['total_entregas']):<25} {'R$ ' + f'{dados['valor_total']:.2f}':<15}")
                print("\n=== Valor Total Acumulado de Todos os Entregadores ===")
                print(f"{'TOTAL GERAL':<15} {'Total de Entregas: ' + str(valores_acumulados['total_entregas_geral']):<25} {'R$ ' + f'{valores_acumulados['total_geral']:.2f}':<15}")
    else:
        print(f"Arquivo '{caminho_arquivo}' não encontrado.")

# Função para adicionar uma entrega ao arquivo
def adicionar_entrega(caminho_arquivo, caminho_acumulado, entregador, dia_entrega, total_entregas):
    if os.path.exists(caminho_arquivo):
        valor_total = total_entregas * 1.5

        # Lendo os valores acumulados atuais
        if os.path.exists(caminho_acumulado):
            with open(caminho_acumulado, 'r') as acumulado:
                valores_acumulados = json.load(acumulado)
        else:
            valores_acumulados = {"total_geral": 0.0, "total_entregas_geral": 0, "entregadores": {}}

        # Atualizando o valor acumulado do entregador
        if entregador in valores_acumulados["entregadores"]:
            valores_acumulados["entregadores"][entregador]["valor_total"] += valor_total
            valores_acumulados["entregadores"][entregador]["total_entregas"] += total_entregas
        else:
            valores_acumulados["entregadores"][entregador] = {"valor_total": valor_total, "total_entregas": total_entregas}

        # Atualizando o valor total geral e total de entregas geral
        valores_acumulados["total_geral"] += valor_total
        valores_acumulados["total_entregas_geral"] += total_entregas

        # Atualizando o arquivo com a nova entrega
        with open(caminho_arquivo, 'a') as arquivo:
            arquivo.write(f"{entregador:<15}     {dia_entrega:<15}       {total_entregas:<20}{'R$ ' + f'{valor_total:.2f}':<15}\n")

        # Salvando os valores acumulados atualizados
        with open(caminho_acumulado, 'w') as acumulado:
            json.dump(valores_acumulados, acumulado)

        print("Entrega adicionada com sucesso.")
    else:
        print(f"Arquivo '{caminho_arquivo}' não encontrado.")
# Função para enviar mensagem pelo WhatsApp com resumo das entregas
def enviar_mensagem_whatsapp(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()
            mensagem_dict = {}

            for linha in linhas[1:]:
                if linha.strip():
                    partes = linha.split()
                    entregador = partes[0]
                    dia_entrega = partes[1]
                    total_entregas = partes[2]

                    if dia_entrega not in mensagem_dict:
                        mensagem_dict[dia_entrega] = {}
                    if entregador not in mensagem_dict[dia_entrega]:
                        mensagem_dict[dia_entrega][entregador] = total_entregas

            while True:
                print("\nEscolha uma opção:")
                print("1. Enviar dados de todos os entregadores")
                print("2. Enviar dados de um entregador específico")
                print("00. Voltar ao menu principal")
                escolha = input("Digite sua escolha: ").strip()

                if escolha == '00':
                    print("Voltando ao menu principal...")
                    break

                if escolha == '1':
                    mensagem = ""
                    total_geral_entregas = {}  # Dicionário para contar total de entregas por entregador

                    for dia, entregadores in mensagem_dict.items():
                        mensagem += f"\nDia da Entrega: {dia}\n"
                        for entregador, total in entregadores.items():
                            mensagem += f"{entregador}\t====\t{total}\n"
                            if entregador in total_geral_entregas:
                                total_geral_entregas[entregador] += int(total)
                            else:
                                total_geral_entregas[entregador] = int(total)

                    # Adiciona o total de entregas de cada entregador na mensagem
                    mensagem += "\nTotal de Entregas por Entregador:\n"
                    for entregador, total in total_geral_entregas.items():
                        mensagem += f"{entregador}:\t{total}\n"
                    mensagem += "\nValor Total:\n"
                    for entregador, total in total_geral_entregas.items():
                        mensagem += f"{entregador}:\tR${total * 1.5:.2f}\n"

                    numero_telefone = input("Digite o número do telefone (com DDI e DDD, ex: +5511999999999): ").strip()
                    if numero_telefone == '00':
                        print("Voltando ao menu principal...")
                        continue
                    else:
                        print('Erro! Por Favor digite um número válido!')

                    try:
                        pywhatkit.sendwhatmsg_instantly(numero_telefone, mensagem)
                        print("Mensagem enviada com sucesso.")
                    except Exception as e:
                        print(f"Erro ao enviar mensagem: {e}")

                elif escolha == '2':
                    entregadores_disponiveis = list({entregador for entregadores in mensagem_dict.values() for entregador in entregadores.keys()})

                    print("\n=== Escolha um entregador ===")
                    for i, entregador in enumerate(entregadores_disponiveis, start=1):
                        print(f"[{i}] {entregador}")

                    print("[00] para voltar")
                    escolha_entregador = input("Escolha o número do entregador: ").strip()

                    if escolha_entregador == '00':
                        print("Voltando ao menu principal...")
                        continue

                    try:
                        escolha_entregador = int(escolha_entregador) - 1
                        entregador_especifico = entregadores_disponiveis[escolha_entregador]
                        mensagem = ""
                        total_entregas_especifico = 0  # Variável para contar total de entregas do entregador específico

                        for dia, entregadores in mensagem_dict.items():
                            if entregador_especifico in entregadores:
                                mensagem += f"\nDia da Entrega: {dia}\n{entregador_especifico} ==== {entregadores[entregador_especifico]}\n"
                                total_entregas_especifico += int(entregadores[entregador_especifico])  # Soma total de entregas do entregador específico
                            
                        mensagem += f"\nTotal de Entregas de {entregador_especifico}: {total_entregas_especifico}\n"  # Adiciona total na mensagem
                        mensagem += f"\nValor Total {entregador_especifico}: R${total_entregas_especifico * 1.5:.2f}"
                        
                        if not mensagem:
                            print(f"Entregador '{entregador_especifico}' não encontrado.")
                            continue

                        numero_telefone = input("Digite o número do telefone (com DDI e DDD, ex: +5511999999999): ").strip()
                        if numero_telefone == '00':
                            print("Voltando ao menu principal...")
                            continue

                        try:
                            pywhatkit.sendwhatmsg_instantly(numero_telefone, mensagem)
                            print("Mensagem enviada com sucesso.")
                        except Exception as e:
                            print(f"Erro ao enviar mensagem: {e}")

                    except (ValueError, IndexError):
                        print("Opção inválida. Tente novamente.")

    else:
        print(f"Arquivo '{caminho_arquivo}' não encontrado.")

 
# Nome do diretório e dos arquivos de entregas e valores acumulados
diretorio = "entregas/01-01 ate 30-01"
nome_arquivo = "entregas.txt"
nome_acumulado = "valores_acumulados.json"

caminho_arquivo = os.path.join(diretorio, nome_arquivo)
caminho_acumulado = os.path.join(diretorio, nome_acumulado)

# Criar arquivos se não existirem
criar_arquivo(diretorio, nome_arquivo, nome_acumulado)

# Loop principal do programa
while True:
    print("\n=== Gerenciamento de Entregas ===")
    print("1. Ver Entregas Cadastradas")
    print("2. Adicionar Entregas")
    print("3. Enviar Mensagem pelo WhatsApp")
    print("4. Sair")
    opcao = input("Escolha uma opção: ").strip()
    if opcao == '1':
        ver_arquivo(caminho_arquivo, caminho_acumulado)

    elif opcao == '2':
            print('[00] Para Voltar ao menu principal')
            dia_entrega = input("Digite o dia da entrega (DD/MM): ").strip()
            if dia_entrega == '00':
                break
            while True:
                entregador = input("Nome do entregador: ").strip().upper()
                if entregador == '00':
                    break
                
                try:
                    total_entregas = int(input("Número total de entregas: "))
                    if total_entregas < 0:
                        print("O número de entregas deve ser positivo.")
                        continue
                except ValueError:
                    print("Por favor, insira um número válido para o total de entregas.")
                    continue
                
                adicionar_entrega(caminho_arquivo, caminho_acumulado, entregador, dia_entrega, total_entregas)

    elif opcao == '3':
        enviar_mensagem_whatsapp(caminho_arquivo)
    elif opcao == '4':
        print("Saindo do sistema...")
        break
    else:
        print("Opção inválida! Por favor, escolha uma opção válida.")


