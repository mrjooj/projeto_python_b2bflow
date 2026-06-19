"""
main.py

Fluxo:
1. Lê até MAX_CONTATOS pessoas cadastradas no Supabase.
2. Para cada uma, envia via Z-API a mensagem:
   "Olá, <nome_contato> tudo bem com você?"
3. Registra logs de sucesso/erro para cada envio.

Uso:
    python main.py
"""
import logging
import sys

from config import ConfigError, load_settings
from supabase_repository import Contato, ContatoRepository
from zapi_client import ZApiClient, ZApiError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

MENSAGEM_TEMPLATE = "Olá, {nome_contato} tudo bem com você?"


def montar_mensagem(contato: Contato) -> str:
    return MENSAGEM_TEMPLATE.format(nome_contato=contato.nome)


def enviar_para_contatos(zapi: ZApiClient, contatos: list[Contato]) -> tuple[int, int]:
    """Envia a mensagem para cada contato. Retorna (sucessos, falhas)."""
    sucessos = 0
    falhas = 0

    for contato in contatos:
        mensagem = montar_mensagem(contato)
        try:
            resultado = zapi.enviar_texto(contato.telefone, mensagem)
            message_id = resultado.get("messageId", "desconhecido")
            logger.info(
                "✅ Mensagem enviada para %s (telefone=%s) | messageId=%s",
                contato.nome, contato.telefone, message_id,
            )
            sucessos += 1
        except ZApiError as exc:
            logger.error(
                "❌ Falha ao enviar para %s (telefone=%s): %s",
                contato.nome, contato.telefone, exc,
            )
            falhas += 1

    return sucessos, falhas


def main() -> int:
    try:
        settings = load_settings()
    except ConfigError as exc:
        logger.error("Erro de configuração: %s", exc)
        return 1

    repo = ContatoRepository(
        url=settings.supabase_url,
        key=settings.supabase_key,
        table=settings.supabase_table,
    )
    zapi = ZApiClient(
        instance_id=settings.zapi_instance_id,
        token=settings.zapi_token,
        client_token=settings.zapi_client_token,
    )

    try:
        contatos = repo.listar_contatos(limite=settings.max_contatos)
    except Exception as exc:  # erro inesperado do SDK do Supabase
        logger.error("Erro ao buscar contatos no Supabase: %s", exc)
        return 1

    if not contatos:
        logger.warning(
            "Nenhum contato válido encontrado na tabela '%s'. "
            "Verifique se a tabela tem registros com 'nome' e 'telefone' preenchidos.",
            settings.supabase_table,
        )
        return 0

    logger.info("Iniciando envio para %d contato(s)...", len(contatos))
    sucessos, falhas = enviar_para_contatos(zapi, contatos)

    logger.info("Concluído. Sucessos: %d | Falhas: %d", sucessos, falhas)
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
