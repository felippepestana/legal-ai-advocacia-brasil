#!/usr/bin/env python3
"""
Assistente Virtual Jurídico com IA
Implementa um assistente conversacional especializado em direito com integração à biblioteca de conhecimento.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from openai import OpenAI

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationType(Enum):
    CONSULTATION = "consultation"
    DOCUMENT_ANALYSIS = "document_analysis"
    JURISPRUDENCE_SEARCH = "jurisprudence_search"
    LEGAL_RESEARCH = "legal_research"
    CASE_STRATEGY = "case_strategy"
    CONTRACT_REVIEW = "contract_review"

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class ConversationMessage:
    message_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class LegalKnowledgeItem:
    item_id: str
    title: str
    content: str
    source: str
    category: str
    tags: List[str]
    relevance_score: float
    created_at: datetime

@dataclass
class ConversationSession:
    session_id: str
    user_id: str
    conversation_type: ConversationType
    title: str
    messages: List[ConversationMessage]
    context_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class LegalKnowledgeBase:
    """Base de conhecimento jurídico com funcionalidades de busca e importação automática."""
    
    def __init__(self):
        self.knowledge_items: Dict[str, LegalKnowledgeItem] = {}
        self.categories = [
            "jurisprudencia", "legislacao", "doutrina", "precedentes",
            "contratos", "peticoes", "sentencas", "acordaos"
        ]
        self._initialize_sample_knowledge()
    
    def _initialize_sample_knowledge(self):
        """Inicializa a base com conhecimento jurídico de exemplo."""
        sample_items = [
            {
                "title": "Súmula 297 do STJ - Código de Defesa do Consumidor",
                "content": "O Código de Defesa do Consumidor é aplicável às instituições financeiras.",
                "source": "STJ - Súmula 297",
                "category": "jurisprudencia",
                "tags": ["cdc", "instituicoes_financeiras", "stj"]
            },
            {
                "title": "Art. 5º da Constituição Federal - Direitos Fundamentais",
                "content": "Todos são iguais perante a lei, sem distinção de qualquer natureza...",
                "source": "Constituição Federal de 1988",
                "category": "legislacao",
                "tags": ["direitos_fundamentais", "igualdade", "constituicao"]
            },
            {
                "title": "Precedente - Revisão de Contratos Bancários",
                "content": "É possível a revisão de contratos bancários quando há cláusulas abusivas...",
                "source": "TJSP - Apelação 1234567-89.2023.8.26.0100",
                "category": "precedentes",
                "tags": ["contratos_bancarios", "clausulas_abusivas", "revisao"]
            }
        ]
        
        for item_data in sample_items:
            item = LegalKnowledgeItem(
                item_id=str(uuid.uuid4()),
                title=item_data["title"],
                content=item_data["content"],
                source=item_data["source"],
                category=item_data["category"],
                tags=item_data["tags"],
                relevance_score=1.0,
                created_at=datetime.now()
            )
            self.knowledge_items[item.item_id] = item
    
    def search_knowledge(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[LegalKnowledgeItem]:
        """Busca itens na base de conhecimento."""
        query_lower = query.lower()
        results = []
        
        for item in self.knowledge_items.values():
            score = 0
            
            # Busca no título
            if query_lower in item.title.lower():
                score += 3
            
            # Busca no conteúdo
            if query_lower in item.content.lower():
                score += 2
            
            # Busca nas tags
            for tag in item.tags:
                if query_lower in tag.lower():
                    score += 1
            
            # Filtro por categoria
            if category and item.category != category:
                continue
            
            if score > 0:
                item.relevance_score = score
                results.append(item)
        
        # Ordenar por relevância
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def add_knowledge_item(self, title: str, content: str, source: str, category: str, tags: List[str]) -> str:
        """Adiciona um novo item à base de conhecimento."""
        item = LegalKnowledgeItem(
            item_id=str(uuid.uuid4()),
            title=title,
            content=content,
            source=source,
            category=category,
            tags=tags,
            relevance_score=1.0,
            created_at=datetime.now()
        )
        
        self.knowledge_items[item.item_id] = item
        logger.info(f"Item adicionado à base de conhecimento: {title}")
        return item.item_id
    
    def import_jurisprudence_automatically(self, keywords: List[str]) -> List[str]:
        """Simula importação automática de jurisprudência."""
        imported_items = []
        
        for keyword in keywords:
            # Simular busca em tribunais
            mock_results = [
                {
                    "title": f"Jurisprudência sobre {keyword} - STJ",
                    "content": f"Decisão relevante sobre {keyword} do Superior Tribunal de Justiça...",
                    "source": "STJ - REsp 1234567",
                    "category": "jurisprudencia",
                    "tags": [keyword.lower(), "stj", "automatico"]
                },
                {
                    "title": f"Precedente {keyword} - TJSP",
                    "content": f"Precedente do Tribunal de Justiça de São Paulo sobre {keyword}...",
                    "source": "TJSP - Apelação 9876543",
                    "category": "precedentes",
                    "tags": [keyword.lower(), "tjsp", "automatico"]
                }
            ]
            
            for result in mock_results:
                item_id = self.add_knowledge_item(
                    result["title"],
                    result["content"],
                    result["source"],
                    result["category"],
                    result["tags"]
                )
                imported_items.append(item_id)
        
        logger.info(f"Importados {len(imported_items)} itens automaticamente")
        return imported_items

class LegalAIAssistant:
    """Assistente de IA especializado em direito."""
    
    def __init__(self, knowledge_base: LegalKnowledgeBase):
        self.client = OpenAI()
        self.knowledge_base = knowledge_base
        self.conversations: Dict[str, ConversationSession] = {}
        
        # Prompt base do sistema
        self.system_prompt = """
        Você é um assistente jurídico especializado em direito brasileiro. Suas características:
        
        1. EXPERTISE: Conhecimento profundo em todas as áreas do direito brasileiro
        2. PRECISÃO: Sempre cite fontes e fundamentos legais
        3. ÉTICA: Nunca forneça conselhos que possam ser considerados exercício ilegal da advocacia
        4. CLAREZA: Explique conceitos complexos de forma acessível
        5. ATUALIZAÇÃO: Considere sempre a legislação e jurisprudência mais recentes
        
        Quando necessário, consulte a base de conhecimento fornecida e cite as fontes.
        Sempre indique quando uma resposta requer análise mais aprofundada por um advogado.
        """
    
    def create_conversation(self, user_id: str, conversation_type: ConversationType, title: str = None) -> str:
        """Cria uma nova sessão de conversa."""
        session_id = str(uuid.uuid4())
        
        if not title:
            title = f"Conversa {conversation_type.value} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            conversation_type=conversation_type,
            title=title,
            messages=[],
            context_data={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Adicionar mensagem do sistema
        system_message = ConversationMessage(
            message_id=str(uuid.uuid4()),
            role=MessageRole.SYSTEM,
            content=self.system_prompt,
            timestamp=datetime.now()
        )
        session.messages.append(system_message)
        
        self.conversations[session_id] = session
        logger.info(f"Nova conversa criada: {session_id} - {title}")
        return session_id
    
    def send_message(self, session_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Envia uma mensagem para o assistente e retorna a resposta."""
        session = self.conversations.get(session_id)
        if not session:
            raise ValueError(f"Sessão {session_id} não encontrada")
        
        # Adicionar mensagem do usuário
        user_message = ConversationMessage(
            message_id=str(uuid.uuid4()),
            role=MessageRole.USER,
            content=message,
            timestamp=datetime.now(),
            metadata=context
        )
        session.messages.append(user_message)
        
        # Buscar conhecimento relevante
        relevant_knowledge = self.knowledge_base.search_knowledge(message, limit=3)
        
        # Construir contexto para a IA
        knowledge_context = ""
        if relevant_knowledge:
            knowledge_context = "\n\nCONHECIMENTO RELEVANTE DA BASE:\n"
            for item in relevant_knowledge:
                knowledge_context += f"- {item.title}: {item.content} (Fonte: {item.source})\n"
        
        # Preparar mensagens para a API
        api_messages = []
        for msg in session.messages[-10:]:  # Últimas 10 mensagens para contexto
            if msg.role != MessageRole.SYSTEM:
                api_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        # Adicionar contexto de conhecimento à última mensagem
        if api_messages:
            api_messages[-1]["content"] += knowledge_context
        
        try:
            # Chamar API da OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "system", "content": self.system_prompt}] + api_messages,
                temperature=0.3,
                max_tokens=1500
            )
            
            assistant_response = response.choices[0].message.content
            
            # Adicionar resposta do assistente
            assistant_message = ConversationMessage(
                message_id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=assistant_response,
                timestamp=datetime.now(),
                metadata={"knowledge_used": [item.item_id for item in relevant_knowledge]}
            )
            session.messages.append(assistant_message)
            
            # Atualizar sessão
            session.updated_at = datetime.now()
            if context:
                session.context_data.update(context)
            
            logger.info(f"Resposta gerada para sessão {session_id}")
            return assistant_response
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            error_response = "Desculpe, ocorreu um erro ao processar sua solicitação. Tente novamente ou reformule sua pergunta."
            
            # Adicionar mensagem de erro
            error_message = ConversationMessage(
                message_id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=error_response,
                timestamp=datetime.now(),
                metadata={"error": str(e)}
            )
            session.messages.append(error_message)
            
            return error_response
    
    def analyze_document_with_assistant(self, session_id: str, document_path: str, analysis_type: str = "general") -> str:
        """Analisa um documento usando o assistente de IA."""
        try:
            # Ler documento (simplificado)
            if document_path.endswith('.txt'):
                with open(document_path, 'r', encoding='utf-8') as f:
                    document_content = f.read()
            else:
                document_content = "Conteúdo do documento não pôde ser extraído."
            
            # Preparar prompt de análise
            analysis_prompt = f"""
            Por favor, analise o seguinte documento jurídico:
            
            TIPO DE ANÁLISE: {analysis_type}
            
            DOCUMENTO:
            {document_content[:3000]}  # Limitar para evitar excesso de tokens
            
            Forneça uma análise detalhada incluindo:
            1. Tipo de documento identificado
            2. Principais pontos jurídicos
            3. Possíveis riscos ou oportunidades
            4. Recomendações práticas
            5. Fundamentos legais aplicáveis
            """
            
            return self.send_message(session_id, analysis_prompt, {
                "document_path": document_path,
                "analysis_type": analysis_type
            })
            
        except Exception as e:
            logger.error(f"Erro na análise de documento: {e}")
            return f"Erro ao analisar documento: {str(e)}"
    
    def search_jurisprudence(self, session_id: str, query: str, court: Optional[str] = None) -> str:
        """Busca jurisprudência usando o assistente."""
        # Buscar na base de conhecimento
        results = self.knowledge_base.search_knowledge(query, "jurisprudencia")
        
        # Importar automaticamente se poucos resultados
        if len(results) < 2:
            keywords = query.split()[:3]  # Primeiras 3 palavras
            self.knowledge_base.import_jurisprudence_automatically(keywords)
            results = self.knowledge_base.search_knowledge(query, "jurisprudencia")
        
        # Preparar prompt
        jurisprudence_prompt = f"""
        Preciso de jurisprudência sobre: {query}
        {f"Tribunal específico: {court}" if court else ""}
        
        Com base nos resultados encontrados na base de conhecimento, forneça:
        1. Resumo das decisões mais relevantes
        2. Tendência jurisprudencial atual
        3. Argumentos principais utilizados pelos tribunais
        4. Aplicabilidade prática para casos similares
        """
        
        return self.send_message(session_id, jurisprudence_prompt, {
            "search_query": query,
            "court": court,
            "results_found": len(results)
        })
    
    def get_conversation_history(self, session_id: str) -> Optional[ConversationSession]:
        """Obtém o histórico de uma conversa."""
        return self.conversations.get(session_id)
    
    def list_conversations(self, user_id: str) -> List[ConversationSession]:
        """Lista conversas de um usuário."""
        return [session for session in self.conversations.values() 
                if session.user_id == user_id and session.is_active]
    
    def export_conversation(self, session_id: str, file_path: str):
        """Exporta uma conversa para arquivo."""
        session = self.conversations.get(session_id)
        if not session:
            raise ValueError(f"Sessão {session_id} não encontrada")
        
        # Converter para dicionário
        session_dict = asdict(session)
        
        # Converter enums e datetime para strings
        session_dict['conversation_type'] = session.conversation_type.value
        session_dict['created_at'] = session.created_at.isoformat()
        session_dict['updated_at'] = session.updated_at.isoformat()
        
        for message in session_dict['messages']:
            message['role'] = MessageRole(message['role']).value
            message['timestamp'] = datetime.fromisoformat(message['timestamp']).isoformat()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Conversa exportada para: {file_path}")

def main():
    """Função principal para demonstração."""
    # Inicializar componentes
    knowledge_base = LegalKnowledgeBase()
    assistant = LegalAIAssistant(knowledge_base)
    
    # Criar sessão de conversa
    session_id = assistant.create_conversation(
        user_id="user123",
        conversation_type=ConversationType.CONSULTATION,
        title="Consulta sobre Direito do Consumidor"
    )
    
    print(f"Sessão criada: {session_id}")
    
    # Simular conversa
    questions = [
        "Quais são os direitos básicos do consumidor?",
        "Como funciona a aplicação do CDC em instituições financeiras?",
        "Posso cancelar um contrato de financiamento dentro de 7 dias?"
    ]
    
    for question in questions:
        print(f"\nUsuário: {question}")
        response = assistant.send_message(session_id, question)
        print(f"Assistente: {response[:200]}...")  # Primeiros 200 caracteres
    
    # Buscar jurisprudência
    print(f"\nBuscando jurisprudência...")
    jurisprudence_response = assistant.search_jurisprudence(
        session_id, 
        "direito do consumidor instituições financeiras"
    )
    print(f"Jurisprudência: {jurisprudence_response[:200]}...")
    
    # Exportar conversa
    export_path = "/home/ubuntu/conversa_assistente_exemplo.json"
    assistant.export_conversation(session_id, export_path)
    print(f"Conversa exportada para: {export_path}")
    
    # Estatísticas
    session = assistant.get_conversation_history(session_id)
    if session:
        print(f"\nEstatísticas da conversa:")
        print(f"- Total de mensagens: {len(session.messages)}")
        print(f"- Tipo: {session.conversation_type.value}")
        print(f"- Duração: {session.updated_at - session.created_at}")

if __name__ == "__main__":
    main()

