#!/usr/bin/env python3
"""
Test Runner para Protótipos de IA Jurídica
Executa testes técnicos e funcionais para validar os protótipos.
"""

import os
import sys
import time
import json
import unittest
from datetime import datetime
from typing import Dict, List, Any

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append('/home/ubuntu')

try:
    from document_analyzer import DocumentAnalyzer, DocumentType
    from workflow_automation import WorkflowEngine, WorkflowBuilder, TriggerType, ActionType
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que os arquivos document_analyzer.py e workflow_automation.py estão no diretório correto.")
    sys.exit(1)

class TestResults:
    """Classe para armazenar e gerenciar resultados dos testes."""
    
    def __init__(self):
        self.results = {
            'document_analysis': {
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'performance_metrics': {},
                'errors': []
            },
            'workflow_automation': {
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'performance_metrics': {},
                'errors': []
            },
            'overall': {
                'start_time': None,
                'end_time': None,
                'total_duration': 0
            }
        }
    
    def add_test_result(self, module: str, test_name: str, passed: bool, duration: float = 0, error: str = None):
        """Adiciona resultado de um teste."""
        self.results[module]['tests_run'] += 1
        if passed:
            self.results[module]['tests_passed'] += 1
        else:
            self.results[module]['tests_failed'] += 1
            if error:
                self.results[module]['errors'].append(f"{test_name}: {error}")
        
        if duration > 0:
            if 'durations' not in self.results[module]['performance_metrics']:
                self.results[module]['performance_metrics']['durations'] = {}
            self.results[module]['performance_metrics']['durations'][test_name] = duration
    
    def save_results(self, filepath: str):
        """Salva os resultados em arquivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)

class DocumentAnalysisTests:
    """Testes para o módulo de análise de documentos."""
    
    def __init__(self, test_results: TestResults):
        self.test_results = test_results
        self.analyzer = DocumentAnalyzer()
        self.test_docs_path = "/home/ubuntu/test_environment/datasets/documentos_de_teste"
    
    def run_all_tests(self):
        """Executa todos os testes de análise de documentos."""
        print("\n=== Executando Testes de Análise de Documentos ===")
        
        self.test_document_classification()
        self.test_entity_extraction()
        self.test_analysis_performance()
        self.test_error_handling()
    
    def test_document_classification(self):
        """Testa a classificação de tipos de documento."""
        print("Testando classificação de documentos...")
        
        test_cases = [
            ("peticao_simples.txt", DocumentType.PETICAO_INICIAL),
            ("contestacao_complexa.txt", DocumentType.CONTESTACAO),
            ("sentenca_procedente.txt", DocumentType.SENTENCA),
            ("intimacao_prazo.txt", DocumentType.INTIMACAO),
            ("documento_sem_tipo.txt", DocumentType.OUTROS)
        ]
        
        for filename, expected_type in test_cases:
            start_time = time.time()
            try:
                filepath = os.path.join(self.test_docs_path, filename)
                if not os.path.exists(filepath):
                    self.test_results.add_test_result(
                        'document_analysis', 
                        f'classification_{filename}', 
                        False, 
                        error=f"Arquivo não encontrado: {filepath}"
                    )
                    continue
                
                analysis = self.analyzer.analyze_document(filepath)
                duration = time.time() - start_time
                
                passed = analysis.document_type == expected_type
                self.test_results.add_test_result(
                    'document_analysis', 
                    f'classification_{filename}', 
                    passed, 
                    duration
                )
                
                if passed:
                    print(f"  ✓ {filename}: {analysis.document_type.value} (confiança: {analysis.confidence_score:.2f})")
                else:
                    print(f"  ✗ {filename}: esperado {expected_type.value}, obtido {analysis.document_type.value}")
                    
            except Exception as e:
                duration = time.time() - start_time
                self.test_results.add_test_result(
                    'document_analysis', 
                    f'classification_{filename}', 
                    False, 
                    duration, 
                    str(e)
                )
                print(f"  ✗ {filename}: Erro - {e}")
    
    def test_entity_extraction(self):
        """Testa a extração de entidades."""
        print("Testando extração de entidades...")
        
        test_cases = [
            ("peticao_simples.txt", ["cpf", "cnpj", "valor_monetario", "data"]),
            ("contestacao_complexa.txt", ["processo"]),
            ("sentenca_procedente.txt", ["processo", "valor_monetario", "data"])
        ]
        
        for filename, expected_entities in test_cases:
            start_time = time.time()
            try:
                filepath = os.path.join(self.test_docs_path, filename)
                analysis = self.analyzer.analyze_document(filepath)
                duration = time.time() - start_time
                
                extracted_types = [entity.type for entity in analysis.extracted_entities]
                found_expected = sum(1 for entity_type in expected_entities if entity_type in extracted_types)
                
                passed = found_expected >= len(expected_entities) * 0.7  # 70% de acerto mínimo
                self.test_results.add_test_result(
                    'document_analysis', 
                    f'entities_{filename}', 
                    passed, 
                    duration
                )
                
                if passed:
                    print(f"  ✓ {filename}: {found_expected}/{len(expected_entities)} entidades encontradas")
                else:
                    print(f"  ✗ {filename}: apenas {found_expected}/{len(expected_entities)} entidades encontradas")
                    
            except Exception as e:
                duration = time.time() - start_time
                self.test_results.add_test_result(
                    'document_analysis', 
                    f'entities_{filename}', 
                    False, 
                    duration, 
                    str(e)
                )
                print(f"  ✗ {filename}: Erro - {e}")
    
    def test_analysis_performance(self):
        """Testa a performance da análise."""
        print("Testando performance da análise...")
        
        filepath = os.path.join(self.test_docs_path, "peticao_simples.txt")
        durations = []
        
        # Executar múltiplas análises para medir performance
        for i in range(5):
            start_time = time.time()
            try:
                analysis = self.analyzer.analyze_document(filepath, f"test_performance_{i}")
                duration = time.time() - start_time
                durations.append(duration)
            except Exception as e:
                print(f"  ✗ Teste de performance {i}: Erro - {e}")
                continue
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            # Critério: análise deve ser concluída em menos de 15 segundos
            passed = avg_duration < 15.0
            
            self.test_results.add_test_result(
                'document_analysis', 
                'performance_test', 
                passed, 
                avg_duration
            )
            
            # Armazenar métricas detalhadas
            self.test_results.results['document_analysis']['performance_metrics'].update({
                'avg_duration': avg_duration,
                'max_duration': max_duration,
                'min_duration': min_duration,
                'samples': len(durations)
            })
            
            if passed:
                print(f"  ✓ Performance: {avg_duration:.2f}s (média), {max_duration:.2f}s (máx)")
            else:
                print(f"  ✗ Performance: {avg_duration:.2f}s (média) - acima do limite de 15s")
        else:
            self.test_results.add_test_result(
                'document_analysis', 
                'performance_test', 
                False, 
                error="Nenhuma análise foi concluída com sucesso"
            )
    
    def test_error_handling(self):
        """Testa o tratamento de erros."""
        print("Testando tratamento de erros...")
        
        # Teste com arquivo inexistente
        start_time = time.time()
        try:
            self.analyzer.analyze_document("/arquivo/inexistente.txt")
            # Se chegou aqui, o teste falhou (deveria ter dado erro)
            self.test_results.add_test_result(
                'document_analysis', 
                'error_handling_missing_file', 
                False, 
                time.time() - start_time,
                "Deveria ter falhado com arquivo inexistente"
            )
            print("  ✗ Arquivo inexistente: não gerou erro como esperado")
        except Exception:
            # Erro esperado
            self.test_results.add_test_result(
                'document_analysis', 
                'error_handling_missing_file', 
                True, 
                time.time() - start_time
            )
            print("  ✓ Arquivo inexistente: erro tratado corretamente")

class WorkflowAutomationTests:
    """Testes para o módulo de automação de workflows."""
    
    def __init__(self, test_results: TestResults):
        self.test_results = test_results
        self.engine = WorkflowEngine()
    
    def run_all_tests(self):
        """Executa todos os testes de automação de workflows."""
        print("\n=== Executando Testes de Automação de Workflows ===")
        
        self.test_workflow_creation()
        self.test_workflow_execution()
        self.test_workflow_performance()
        self.test_error_handling()
    
    def test_workflow_creation(self):
        """Testa a criação de workflows."""
        print("Testando criação de workflows...")
        
        start_time = time.time()
        try:
            # Criar workflow de teste
            workflow = (WorkflowBuilder("Teste de Criação", "Workflow para teste")
                       .add_trigger(TriggerType.MANUAL_TRIGGER, {}, "Gatilho manual")
                       .add_action(ActionType.SEND_NOTIFICATION, 
                                 {'title': 'Teste', 'message': 'Mensagem de teste'}, 
                                 "Notificação de teste")
                       .build("test_user"))
            
            workflow_id = self.engine.register_workflow(workflow)
            duration = time.time() - start_time
            
            passed = workflow_id is not None and workflow_id in self.engine.workflows
            self.test_results.add_test_result(
                'workflow_automation', 
                'workflow_creation', 
                passed, 
                duration
            )
            
            if passed:
                print(f"  ✓ Workflow criado com sucesso: {workflow_id}")
            else:
                print("  ✗ Falha na criação do workflow")
                
        except Exception as e:
            duration = time.time() - start_time
            self.test_results.add_test_result(
                'workflow_automation', 
                'workflow_creation', 
                False, 
                duration, 
                str(e)
            )
            print(f"  ✗ Erro na criação: {e}")
    
    def test_workflow_execution(self):
        """Testa a execução de workflows."""
        print("Testando execução de workflows...")
        
        # Criar workflow para teste
        workflow = (WorkflowBuilder("Teste de Execução", "Workflow para teste de execução")
                   .add_trigger(TriggerType.MANUAL_TRIGGER, {}, "Gatilho manual")
                   .add_action(ActionType.SEND_NOTIFICATION, 
                             {'title': 'Teste Execução', 'message': 'Workflow executado'}, 
                             "Notificação de execução")
                   .add_action(ActionType.CREATE_TASK, 
                             {'title': 'Tarefa de Teste', 'description': 'Tarefa criada pelo workflow'}, 
                             "Criação de tarefa")
                   .build("test_user"))
        
        workflow_id = self.engine.register_workflow(workflow)
        
        start_time = time.time()
        try:
            # Executar workflow
            execution_id = self.engine.trigger_workflow(workflow_id, {'test': True})
            
            # Aguardar conclusão
            time.sleep(2)
            
            execution = self.engine.get_execution_status(execution_id)
            duration = time.time() - start_time
            
            passed = (execution is not None and 
                     execution.status == "completed" and 
                     len(execution.actions_executed) == 2)
            
            self.test_results.add_test_result(
                'workflow_automation', 
                'workflow_execution', 
                passed, 
                duration
            )
            
            if passed:
                print(f"  ✓ Workflow executado com sucesso: {execution.status}")
                print(f"    Ações executadas: {len(execution.actions_executed)}")
            else:
                print(f"  ✗ Falha na execução: status={execution.status if execution else 'None'}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.test_results.add_test_result(
                'workflow_automation', 
                'workflow_execution', 
                False, 
                duration, 
                str(e)
            )
            print(f"  ✗ Erro na execução: {e}")
    
    def test_workflow_performance(self):
        """Testa a performance dos workflows."""
        print("Testando performance dos workflows...")
        
        # Criar workflow simples para teste de performance
        workflow = (WorkflowBuilder("Teste Performance", "Workflow para teste de performance")
                   .add_trigger(TriggerType.MANUAL_TRIGGER, {}, "Gatilho manual")
                   .add_action(ActionType.SEND_NOTIFICATION, 
                             {'title': 'Performance', 'message': 'Teste de performance'}, 
                             "Notificação rápida")
                   .build("test_user"))
        
        workflow_id = self.engine.register_workflow(workflow)
        
        durations = []
        successful_executions = 0
        
        # Executar múltiplos workflows para medir performance
        for i in range(10):
            start_time = time.time()
            try:
                execution_id = self.engine.trigger_workflow(workflow_id, {'test_run': i})
                time.sleep(0.5)  # Aguardar execução
                
                execution = self.engine.get_execution_status(execution_id)
                duration = time.time() - start_time
                
                if execution and execution.status == "completed":
                    durations.append(duration)
                    successful_executions += 1
                    
            except Exception as e:
                print(f"    Erro na execução {i}: {e}")
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            success_rate = successful_executions / 10
            
            # Critérios: 95% de sucesso e tempo médio < 5 segundos
            passed = success_rate >= 0.95 and avg_duration < 5.0
            
            self.test_results.add_test_result(
                'workflow_automation', 
                'performance_test', 
                passed, 
                avg_duration
            )
            
            # Armazenar métricas detalhadas
            self.test_results.results['workflow_automation']['performance_metrics'].update({
                'avg_duration': avg_duration,
                'success_rate': success_rate,
                'successful_executions': successful_executions,
                'total_attempts': 10
            })
            
            if passed:
                print(f"  ✓ Performance: {avg_duration:.2f}s (média), {success_rate:.1%} sucesso")
            else:
                print(f"  ✗ Performance: {avg_duration:.2f}s (média), {success_rate:.1%} sucesso")
        else:
            self.test_results.add_test_result(
                'workflow_automation', 
                'performance_test', 
                False, 
                error="Nenhuma execução foi bem-sucedida"
            )
    
    def test_error_handling(self):
        """Testa o tratamento de erros."""
        print("Testando tratamento de erros...")
        
        start_time = time.time()
        try:
            # Tentar executar workflow inexistente
            self.engine.trigger_workflow("workflow_inexistente", {})
            # Se chegou aqui, o teste falhou
            self.test_results.add_test_result(
                'workflow_automation', 
                'error_handling_missing_workflow', 
                False, 
                time.time() - start_time,
                "Deveria ter falhado com workflow inexistente"
            )
            print("  ✗ Workflow inexistente: não gerou erro como esperado")
        except Exception:
            # Erro esperado
            self.test_results.add_test_result(
                'workflow_automation', 
                'error_handling_missing_workflow', 
                True, 
                time.time() - start_time
            )
            print("  ✓ Workflow inexistente: erro tratado corretamente")

def main():
    """Função principal para executar todos os testes."""
    print("=== INICIANDO TESTES TÉCNICOS E FUNCIONAIS ===")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Inicializar resultados
    test_results = TestResults()
    test_results.results['overall']['start_time'] = datetime.now()
    
    # Executar testes de análise de documentos
    doc_tests = DocumentAnalysisTests(test_results)
    doc_tests.run_all_tests()
    
    # Executar testes de automação de workflows
    workflow_tests = WorkflowAutomationTests(test_results)
    workflow_tests.run_all_tests()
    
    # Finalizar
    test_results.results['overall']['end_time'] = datetime.now()
    test_results.results['overall']['total_duration'] = (
        test_results.results['overall']['end_time'] - 
        test_results.results['overall']['start_time']
    ).total_seconds()
    
    # Salvar resultados
    results_file = "/home/ubuntu/test_environment/test_results.json"
    test_results.save_results(results_file)
    
    # Exibir resumo
    print("\n=== RESUMO DOS TESTES ===")
    
    for module in ['document_analysis', 'workflow_automation']:
        results = test_results.results[module]
        total = results['tests_run']
        passed = results['tests_passed']
        failed = results['tests_failed']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{module.replace('_', ' ').title()}:")
        print(f"  Total de testes: {total}")
        print(f"  Sucessos: {passed}")
        print(f"  Falhas: {failed}")
        print(f"  Taxa de sucesso: {success_rate:.1f}%")
        
        if results['errors']:
            print("  Erros:")
            for error in results['errors']:
                print(f"    - {error}")
    
    total_duration = test_results.results['overall']['total_duration']
    print(f"\nDuração total dos testes: {total_duration:.2f} segundos")
    print(f"Resultados salvos em: {results_file}")

if __name__ == "__main__":
    main()

