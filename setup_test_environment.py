'''
Script para configurar o ambiente de testes e gerar dados de validação.
'''

import os
import json


def create_test_documents():
    """Cria um conjunto de documentos de teste para validação."""
    test_docs_path = "/home/ubuntu/test_environment/datasets/documentos_de_teste"
    if not os.path.exists(test_docs_path):
        os.makedirs(test_docs_path)

    documents = {
        "peticao_simples.txt": """
        PETIÇÃO INICIAL

        Ação de Cobrança

        Autor: JOÃO DA SILVA, CPF 111.222.333-44
        Réu: EMPRESA ABC LTDA, CNPJ 99.888.777/0001-66

        Valor da causa: R$ 10.000,00
        Data: 01/08/2025
        """,
        "contestacao_complexa.txt": """
        CONTESTAÇÃO

        Processo n° 0012345-67.2025.8.26.0100

        Contestante: EMPRESA ABC LTDA
        Contestado: JOÃO DA SILVA

        PRELIMINARMENTE, argui-se a ilegitimidade passiva.
        No mérito, impugna-se o valor cobrado.
        Prazo para réplica: 15 dias.
        """,
        "sentenca_procedente.txt": """
        SENTENÇA

        Processo n° 0012345-67.2025.8.26.0100

        Ante o exposto, JULGO PROCEDENTE o pedido para condenar a ré ao pagamento de R$ 8.500,00.
        Custas e honorários pela ré.
        Publique-se. Registre-se. Intimem-se.
        São Paulo, 10/09/2025.
        """,
        "documento_sem_tipo.txt": """
        Relatório de Atividades

        Este é um documento interno para controle de tarefas.
        Nenhuma ação judicial necessária.
        """,
        "intimacao_prazo.txt": """
        INTIMAÇÃO

        Fica a parte autora intimada a se manifestar sobre a contestação no prazo de 15 (quinze) dias.
        """
    }

    for filename, content in documents.items():
        with open(os.path.join(test_docs_path, filename), "w", encoding="utf-8") as f:
            f.write(content)
    print(f"{len(documents)} documentos de teste criados em {test_docs_path}")


def main():
    """Função principal para configurar o ambiente."""
    print("Iniciando configuração do ambiente de testes...")
    create_test_documents()
    print("Ambiente de testes configurado com sucesso!")


if __name__ == "__main__":
    main()


