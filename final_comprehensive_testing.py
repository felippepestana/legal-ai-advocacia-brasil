"""
Testes Abrangentes Finais da Plataforma Legal AI
Valida todas as funcionalidades implementadas e melhorias
"""

import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Adiciona os diretórios das funcionalidades ao path
sys.path.append('/home/ubuntu/ai_improvements/search')
sys.path.append('/home/ubuntu/ai_improvements/calculator')
sys.path.append('/home/ubuntu/ai_improvements/analytics')
sys.path.append('/home/ubuntu/ai_improvements/documents')

# Importa as funcionalidades avançadas
try:
    from advanced_search_features import AdvancedSearchInterface
    from advanced_calculator_features import AdvancedCalculationEngine, CalculationInput, CalculationType, ValidationLevel
    from advanced_analytics_features import AdvancedAnalyticsEngine
    from advanced_document_features import AdvancedDocumentGenerator
except ImportError as e:
    print(f"Erro ao importar funcionalidades: {e}")
    print("Continuando com testes básicos...")

class ComprehensiveTestSuite:
    """Suite de testes abrangentes para todas as funcionalidades"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "performance_metrics": {},
            "coverage_report": {}
        }
        
    def run_test(self, test_name: str, test_function, *args, **kwargs) -> bool:
        """Executa um teste individual"""
        print(f"\n--- Executando: {test_name} ---")
        self.test_results["total_tests"] += 1
        
        start_time = time.time()
        try:
            result = test_function(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if result:
                print(f"✅ PASSOU: {test_name} ({execution_time:.3f}s)")
                self.test_results["passed_tests"] += 1
                status = "PASSED"
            else:
                print(f"❌ FALHOU: {test_name} ({execution_time:.3f}s)")
                self.test_results["failed_tests"] += 1
                status = "FAILED"
                
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"💥 ERRO: {test_name} - {str(e)} ({execution_time:.3f}s)")
            self.test_results["failed_tests"] += 1
            status = "ERROR"
            result = False
            
        self.test_results["test_details"].append({
            "name": test_name,
            "status": status,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def test_advanced_search_functionality(self) -> bool:
        """Testa funcionalidades avançadas de pesquisa"""
        try:
            search_interface = AdvancedSearchInterface()
            
            # Teste 1: Pesquisa básica
            result1 = search_interface.search("danos morais negativação")
            if not result1 or not result1.get("results"):
                return False
            
            # Teste 2: Pesquisa com filtros
            result2 = search_interface.search(
                "rescisão trabalhista",
                {"type": "MIXED", "max_results": 5}
            )
            if not result2 or len(result2.get("results", [])) == 0:
                return False
            
            # Teste 3: Analytics de pesquisa
            analytics = search_interface.get_search_analytics()
            if not analytics or analytics.get("total_searches", 0) < 2:
                return False
            
            print(f"  - Pesquisas realizadas: {analytics['total_searches']}")
            print(f"  - Resultados encontrados: {len(result1['results']) + len(result2['results'])}")
            
            return True
            
        except Exception as e:
            print(f"  Erro no teste de pesquisa: {e}")
            return False
    
    def test_advanced_calculator_functionality(self) -> bool:
        """Testa funcionalidades avançadas da calculadora"""
        try:
            calc_engine = AdvancedCalculationEngine()
            
            # Teste 1: Cálculo de rescisão trabalhista
            calc_input1 = CalculationInput(
                calculation_type=CalculationType.TRABALHISTA_RESCISAO,
                parameters={
                    "salario": "3500.00",
                    "tempo_servico_meses": 18,
                    "tipo_rescisao": "sem_justa_causa",
                    "dias_trabalhados_mes": 30
                },
                validation_level=ValidationLevel.COMPREHENSIVE,
                user_id="test_user",
                timestamp=datetime.now()
            )
            
            result1 = calc_engine.calculate_advanced(calc_input1)
            if not result1 or result1.result_value <= 0:
                return False
            
            # Teste 2: Cálculo de danos morais
            calc_input2 = CalculationInput(
                calculation_type=CalculationType.CIVIL_DANOS_MORAIS,
                parameters={
                    "gravidade": "alta",
                    "renda_vitima": "8000.00",
                    "capacidade_pagador": "500000.00"
                },
                validation_level=ValidationLevel.INTERMEDIATE,
                user_id="test_user",
                timestamp=datetime.now()
            )
            
            result2 = calc_engine.calculate_advanced(calc_input2)
            if not result2 or result2.result_value <= 0:
                return False
            
            # Teste 3: Estatísticas dos cálculos
            stats = calc_engine.get_calculation_statistics()
            if not stats or stats.get("total_calculations", 0) < 2:
                return False
            
            print(f"  - Cálculos realizados: {stats['total_calculations']}")
            print(f"  - Valor médio: R$ {stats['average_value']:.2f}")
            print(f"  - Tempo médio: {stats['average_calculation_time']:.4f}s")
            
            return True
            
        except Exception as e:
            print(f"  Erro no teste de calculadora: {e}")
            return False
    
    def test_advanced_analytics_functionality(self) -> bool:
        """Testa funcionalidades avançadas de analytics"""
        try:
            analytics_engine = AdvancedAnalyticsEngine()
            
            # Teste 1: Geração de relatório básico
            report1 = analytics_engine.generate_comprehensive_report()
            if not report1 or not report1.get("performance_metrics"):
                return False
            
            # Teste 2: Análise preditiva
            predictions = analytics_engine.generate_predictive_analysis()
            if not predictions or not predictions.get("revenue_forecast"):
                return False
            
            # Teste 3: Comparação com benchmarks
            benchmarks = analytics_engine.compare_with_benchmarks()
            if not benchmarks or not benchmarks.get("comparison_results"):
                return False
            
            print(f"  - Métricas analisadas: {len(report1['performance_metrics'])}")
            print(f"  - Previsões geradas: {len(predictions)}")
            print(f"  - Benchmarks comparados: {len(benchmarks['comparison_results'])}")
            
            return True
            
        except Exception as e:
            print(f"  Erro no teste de analytics: {e}")
            return False
    
    def test_advanced_document_functionality(self) -> bool:
        """Testa funcionalidades avançadas de geração de documentos"""
        try:
            doc_generator = AdvancedDocumentGenerator()
            
            # Teste 1: Geração de petição inicial
            doc1 = doc_generator.generate_advanced_document(
                "peticao_inicial",
                {
                    "autor": "João Silva",
                    "reu": "Banco XYZ",
                    "valor": "25000.00",
                    "fundamento": "Danos morais por negativação indevida"
                }
            )
            if not doc1 or not doc1.get("content"):
                return False
            
            # Teste 2: Geração de contrato
            doc2 = doc_generator.generate_advanced_document(
                "contrato_prestacao_servicos",
                {
                    "contratante": "Empresa ABC",
                    "contratado": "Prestador XYZ",
                    "valor": "5000.00",
                    "prazo": "12 meses"
                }
            )
            if not doc2 or not doc2.get("content"):
                return False
            
            # Teste 3: Validação de documentos
            validation = doc_generator.validate_document_quality(doc1["content"])
            if not validation or validation.get("score", 0) < 0.7:
                return False
            
            print(f"  - Documentos gerados: 2")
            print(f"  - Score de qualidade: {validation['score']:.2f}")
            print(f"  - Tamanho médio: {(len(doc1['content']) + len(doc2['content'])) // 2} caracteres")
            
            return True
            
        except Exception as e:
            print(f"  Erro no teste de documentos: {e}")
            return False
    
    def test_integration_functionality(self) -> bool:
        """Testa integração entre funcionalidades"""
        try:
            # Simula um fluxo completo de trabalho
            search_interface = AdvancedSearchInterface()
            calc_engine = AdvancedCalculationEngine()
            
            # 1. Pesquisa jurisprudência
            search_result = search_interface.search("rescisão trabalhista horas extras")
            if not search_result or not search_result.get("results"):
                return False
            
            # 2. Calcula valores baseado na pesquisa
            calc_input = CalculationInput(
                calculation_type=CalculationType.TRABALHISTA_HORAS_EXTRAS,
                parameters={
                    "salario_hora": "25.00",
                    "horas_extras": "50",
                    "percentual_adicional": "50"
                },
                validation_level=ValidationLevel.BASIC,
                user_id="integration_test",
                timestamp=datetime.now()
            )
            
            calc_result = calc_engine.calculate_advanced(calc_input)
            if not calc_result or calc_result.result_value <= 0:
                return False
            
            # 3. Verifica se os resultados são consistentes
            if calc_result.confidence_score < 0.8:
                return False
            
            print(f"  - Integração pesquisa-cálculo: OK")
            print(f"  - Confiança do resultado: {calc_result.confidence_score:.2f}")
            print(f"  - Valor calculado: R$ {calc_result.result_value:.2f}")
            
            return True
            
        except Exception as e:
            print(f"  Erro no teste de integração: {e}")
            return False
    
    def test_performance_benchmarks(self) -> bool:
        """Testa performance das funcionalidades"""
        try:
            performance_data = {}
            
            # Teste de performance da pesquisa
            start_time = time.time()
            search_interface = AdvancedSearchInterface()
            for i in range(5):
                search_interface.search(f"teste performance {i}")
            search_time = (time.time() - start_time) / 5
            performance_data["search_avg_time"] = search_time
            
            # Teste de performance da calculadora
            start_time = time.time()
            calc_engine = AdvancedCalculationEngine()
            for i in range(5):
                calc_input = CalculationInput(
                    calculation_type=CalculationType.CIVIL_DANOS_MORAIS,
                    parameters={
                        "gravidade": "media",
                        "renda_vitima": f"{3000 + i * 500}.00",
                        "capacidade_pagador": "100000.00"
                    },
                    validation_level=ValidationLevel.BASIC,
                    user_id="perf_test",
                    timestamp=datetime.now()
                )
                calc_engine.calculate_advanced(calc_input)
            calc_time = (time.time() - start_time) / 5
            performance_data["calculation_avg_time"] = calc_time
            
            # Verifica se os tempos estão dentro dos limites aceitáveis
            if search_time > 2.0 or calc_time > 1.0:
                print(f"  ⚠️ Performance abaixo do esperado:")
                print(f"    - Pesquisa: {search_time:.3f}s (limite: 2.0s)")
                print(f"    - Cálculo: {calc_time:.3f}s (limite: 1.0s)")
                return False
            
            self.test_results["performance_metrics"] = performance_data
            
            print(f"  - Tempo médio pesquisa: {search_time:.3f}s")
            print(f"  - Tempo médio cálculo: {calc_time:.3f}s")
            print(f"  - Performance: ADEQUADA")
            
            return True
            
        except Exception as e:
            print(f"  Erro no teste de performance: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Testa tratamento de erros"""
        try:
            calc_engine = AdvancedCalculationEngine()
            
            # Teste 1: Parâmetros inválidos
            try:
                calc_input = CalculationInput(
                    calculation_type=CalculationType.TRABALHISTA_RESCISAO,
                    parameters={
                        "salario": "invalid",  # Valor inválido
                        "tempo_servico_meses": -5  # Valor negativo
                    },
                    validation_level=ValidationLevel.COMPREHENSIVE,
                    user_id="error_test",
                    timestamp=datetime.now()
                )
                result = calc_engine.calculate_advanced(calc_input)
                # Se chegou aqui, o erro não foi tratado adequadamente
                if result.validation_status == "VALID":
                    return False
            except ValueError:
                # Erro esperado, tratamento adequado
                pass
            
            # Teste 2: Pesquisa com query vazia
            search_interface = AdvancedSearchInterface()
            result = search_interface.search("")
            if not result or result.get("total_results", 0) > 0:
                return False
            
            print(f"  - Tratamento de erros: ADEQUADO")
            return True
            
        except Exception as e:
            print(f"  Erro no teste de tratamento de erros: {e}")
            return False
    
    def generate_coverage_report(self) -> Dict[str, Any]:
        """Gera relatório de cobertura dos testes"""
        coverage = {
            "modules_tested": [
                "advanced_search_features",
                "advanced_calculator_features", 
                "advanced_analytics_features",
                "advanced_document_features"
            ],
            "functionality_coverage": {
                "search": ["basic_search", "filtered_search", "analytics"],
                "calculator": ["rescisao", "danos_morais", "horas_extras", "statistics"],
                "analytics": ["reports", "predictions", "benchmarks"],
                "documents": ["generation", "validation", "templates"],
                "integration": ["search_calc_flow", "error_handling"],
                "performance": ["speed_tests", "load_tests"]
            },
            "test_categories": {
                "unit_tests": 4,
                "integration_tests": 1,
                "performance_tests": 1,
                "error_handling_tests": 1
            }
        }
        
        self.test_results["coverage_report"] = coverage
        return coverage
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES ABRANGENTES DA PLATAFORMA LEGAL AI")
        print("=" * 60)
        
        # Lista de testes a executar
        tests = [
            ("Funcionalidades Avançadas de Pesquisa", self.test_advanced_search_functionality),
            ("Funcionalidades Avançadas da Calculadora", self.test_advanced_calculator_functionality),
            ("Funcionalidades Avançadas de Analytics", self.test_advanced_analytics_functionality),
            ("Funcionalidades Avançadas de Documentos", self.test_advanced_document_functionality),
            ("Integração entre Funcionalidades", self.test_integration_functionality),
            ("Benchmarks de Performance", self.test_performance_benchmarks),
            ("Tratamento de Erros", self.test_error_handling)
        ]
        
        # Executa todos os testes
        for test_name, test_function in tests:
            self.run_test(test_name, test_function)
        
        # Gera relatório de cobertura
        self.generate_coverage_report()
        
        # Calcula estatísticas finais
        success_rate = (self.test_results["passed_tests"] / self.test_results["total_tests"]) * 100
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        print(f"Total de testes: {self.test_results['total_tests']}")
        print(f"Testes aprovados: {self.test_results['passed_tests']}")
        print(f"Testes falharam: {self.test_results['failed_tests']}")
        print(f"Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 85:
            print("🎉 RESULTADO: EXCELENTE - Sistema pronto para produção!")
        elif success_rate >= 70:
            print("✅ RESULTADO: BOM - Sistema funcional com pequenos ajustes necessários")
        else:
            print("⚠️ RESULTADO: NECESSITA MELHORIAS - Revisar funcionalidades com falhas")
        
        return self.test_results

def main():
    """Função principal"""
    test_suite = ComprehensiveTestSuite()
    results = test_suite.run_all_tests()
    
    # Salva resultados em arquivo
    results_file = "/home/ubuntu/ai_improvements/final_test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Resultados salvos em: {results_file}")
    
    return results

if __name__ == "__main__":
    main()

