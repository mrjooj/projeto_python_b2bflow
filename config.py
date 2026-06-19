"""
Módulo de configuração.
Carrega e valida as variáveis de ambiente necessárias para a aplicação.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Erro de configuração de ambiente (variável ausente ou inválida)."""


def _get_required(key: str) -> str:
    value = os.getenv(key)
    if not value or not value.strip():
        raise ConfigError(
            f"Variável de ambiente obrigatória '{key}' não foi definida. "
            f"Verifique seu arquivo .env (veja .env.example)."
        )
    return value.strip()


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_key: str
    supabase_table: str

    zapi_instance_id: str
    zapi_token: str
    zapi_client_token: str

    max_contatos: int


def load_settings() -> Settings:
    """Lê e valida todas as variáveis de ambiente. Lança ConfigError se algo faltar."""
    max_contatos_raw = os.getenv("MAX_CONTATOS", "3")
    try:
        max_contatos = int(max_contatos_raw)
    except ValueError as exc:
        raise ConfigError(
            f"MAX_CONTATOS deve ser um número inteiro. Valor recebido: '{max_contatos_raw}'"
        ) from exc

    if max_contatos < 1:
        raise ConfigError("MAX_CONTATOS deve ser maior ou igual a 1.")

    return Settings(
        supabase_url=_get_required("SUPABASE_URL"),
        supabase_key=_get_required("SUPABASE_KEY"),
        supabase_table=os.getenv("SUPABASE_TABLE", "contatos").strip(),
        zapi_instance_id=_get_required("ZAPI_INSTANCE_ID"),
        zapi_token=_get_required("ZAPI_TOKEN"),
        zapi_client_token=_get_required("ZAPI_CLIENT_TOKEN"),
        max_contatos=max_contatos,
    )
