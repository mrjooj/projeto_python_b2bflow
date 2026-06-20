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
    zapi_delay_typing: int
    zapi_delay_message: int

    max_contatos: int
    intervalo_min_segundos: float
    intervalo_max_segundos: float


def _get_int_in_range(key: str, default: int, minimo: int, maximo: int) -> int:
    """Lê uma variável inteira opcional e garante que está dentro do range [minimo, maximo]."""
    raw = os.getenv(key, str(default))
    try:
        valor = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{key} deve ser um número inteiro. Valor recebido: '{raw}'") from exc

    if not (minimo <= valor <= maximo):
        raise ConfigError(f"{key} deve estar entre {minimo} e {maximo}. Valor recebido: {valor}")
    return valor


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

    # A Z-API aceita de 1 a 15 segundos para delayTyping/delayMessage.
    zapi_delay_typing = _get_int_in_range("ZAPI_DELAY_TYPING", default=3, minimo=1, maximo=15)
    zapi_delay_message = _get_int_in_range("ZAPI_DELAY_MESSAGE", default=2, minimo=1, maximo=15)

    intervalo_min_raw = os.getenv("INTERVALO_MIN_SEGUNDOS", "3")
    intervalo_max_raw = os.getenv("INTERVALO_MAX_SEGUNDOS", "8")
    try:
        intervalo_min_segundos = float(intervalo_min_raw)
        intervalo_max_segundos = float(intervalo_max_raw)
    except ValueError as exc:
        raise ConfigError(
            "INTERVALO_MIN_SEGUNDOS e INTERVALO_MAX_SEGUNDOS devem ser números. "
            f"Valores recebidos: '{intervalo_min_raw}' e '{intervalo_max_raw}'"
        ) from exc

    if intervalo_min_segundos < 0 or intervalo_max_segundos < 0:
        raise ConfigError("Os intervalos não podem ser negativos.")
    if intervalo_min_segundos > intervalo_max_segundos:
        raise ConfigError(
            "INTERVALO_MIN_SEGUNDOS não pode ser maior que INTERVALO_MAX_SEGUNDOS."
        )

    return Settings(
        supabase_url=_get_required("SUPABASE_URL"),
        supabase_key=_get_required("SUPABASE_KEY"),
        supabase_table=os.getenv("SUPABASE_TABLE", "contatos").strip(),
        zapi_instance_id=_get_required("ZAPI_INSTANCE_ID"),
        zapi_token=_get_required("ZAPI_TOKEN"),
        zapi_client_token=_get_required("ZAPI_CLIENT_TOKEN"),
        zapi_delay_typing=zapi_delay_typing,
        zapi_delay_message=zapi_delay_message,
        max_contatos=max_contatos,
        intervalo_min_segundos=intervalo_min_segundos,
        intervalo_max_segundos=intervalo_max_segundos,
    )