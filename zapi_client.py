"""
Cliente HTTP para a Z-API (envio de mensagens de WhatsApp).
Documentação: https://developer.z-api.io/en/message/send-message-text
"""
import logging
import re

import requests

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 15


class ZApiError(Exception):
    """Erro ao se comunicar com a Z-API."""


class ZApiClient:
    def __init__(self, instance_id: str, token: str, client_token: str):
        self._base_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"
        self._headers = {
            "Content-Type": "application/json",
            "Client-Token": client_token,
        }

    def enviar_texto(
        self,
        telefone: str,
        mensagem: str,
        delay_typing: int | None = None,
        delay_message: int | None = None,
    ) -> dict:
        """
        Envia uma mensagem de texto para o telefone informado.

        delay_typing/delay_message (1-15s) são parâmetros nativos da Z-API: o primeiro
        mostra "digitando..." no WhatsApp antes da mensagem chegar, o segundo atrasa
        a entrega. Retorna o JSON de resposta (zaapId, messageId) ou lança ZApiError.
        """
        telefone_normalizado = self._normalizar_telefone(telefone)
        payload = {"phone": telefone_normalizado, "message": mensagem}

        if delay_typing is not None:
            payload["delayTyping"] = delay_typing
        if delay_message is not None:
            payload["delayMessage"] = delay_message

        try:
            response = requests.post(
                self._base_url,
                json=payload,
                headers=self._headers,
                timeout=_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            raise ZApiError(f"Falha de conexão com a Z-API: {exc}") from exc

        if not response.ok:
            raise ZApiError(
                f"Z-API retornou status {response.status_code} para o telefone "
                f"{telefone_normalizado}: {response.text}"
            )

        return response.json()

    @staticmethod
    def _normalizar_telefone(telefone: str) -> str:
        """Remove qualquer caractere que não seja dígito (espaços, +, -, parênteses)."""
        apenas_digitos = re.sub(r"\D", "", telefone)
        if not apenas_digitos:
            raise ZApiError(f"Telefone inválido: '{telefone}'")
        return apenas_digitos