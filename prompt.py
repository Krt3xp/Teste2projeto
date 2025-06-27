from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 1. Definição da estrutura de saída com Pydantic
class OrganizacaoCriminosaExtract(BaseModel):
    """Extração de informações sobre organizações criminosas de um texto."""
    organizacao_criminosa: str = Field(..., description="Nome da organização criminosa. Se não encontrar, retorne 'Não especificado'.")
    pais: str = Field(..., description="País onde o evento ocorreu. Se não encontrar, retorne 'Não especificado'.")
    estado: str = Field(..., description="Sigla do estado onde o evento ocorreu (ex: SP, RJ, GO). Se não encontrar, retorne 'Não especificado'.")
    municipio: str = Field(..., description="Município onde o evento ocorreu. Se não encontrar, retorne 'Não especificado'.")
    data: str = Field(..., description="Data do evento no formato DD-MM-AAAA. Se não encontrar, retorne 'Não especificado'.")
    houve_conflito: str = Field(..., description="Indica se houve conflito armado (Sim ou Não). Se não for claro, retorne 'Não especificado'.")
    apreensao_drogas: str = Field(..., description="Indica se houve apreensão de drogas (Sim ou Não).")
    drogas_apreendidas: List[str] = Field(default_factory=list, description="Lista com os nomes das drogas apreendidas. Se não houver, retorne uma lista vazia.")
    quantidade_drogas: str = Field(..., description="Quantidade de drogas apreendidas (incluir unidade de medida, ex: '10 kg'). Se não encontrar, retorne 'Não especificado'.")
    apreensao_armas: str = Field(..., description="Indica se houve apreensão de armas (Sim ou Não).")
    armas_apreendidas: List[str] = Field(default_factory=list, description="Lista com os nomes das armas apreendidas. Se não houver, retorne uma lista vazia.")
    primeiro_ator: str = Field(..., description="Primeiro ator principal envolvido. Se não for claro, retorne 'Não especificado'.")
    segundo_ator: str = Field(..., description="Segundo ator principal envolvido. Se não for claro, retorne 'Não especificado'.")
    relacao_entre_atores: str = Field(..., description="Relação principal entre os atores (Rivalidade, Competição, Cooperação, Integração, Confronto). Se não for claro, retorne 'Não especificado'.")

# 2. Criação do Parser de JSON
parser = JsonOutputParser(pydantic_object=OrganizacaoCriminosaExtract)

# 3. Criação do Template do Prompt
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é um especialista em análise de notícias sobre criminalidade e segurança pública no Brasil.
Sua tarefa é extrair informações específicas do texto fornecido e retorná-las ESTRITAMENTE no formato JSON solicitado.
Se uma informação não estiver presente no texto, retorne 'Não especificado' ou um valor padrão (como uma lista vazia []), conforme a descrição do campo. Não invente informações.

{format_instructions}
""",
        ),
        (
            "human",
            "Aqui está a notícia para análise:\n\n---\n\n{input_noticia}"
        ),
    ]
).partial(format_instructions=parser.get_format_instructions())