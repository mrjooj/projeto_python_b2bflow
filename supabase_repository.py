"""Busca os contatos cadastrados na tabela do Supabase."""
import logging
from dataclasses import dataclass

from supabase import Client, create_client

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Contato:
    id: str
    nome: str
    telefone: str


class ContatoRepository:
    """Acesso à tabela de contatos no Supabase."""

    def __init__(self, url: str, key: str, table: str):
        self._table = table
        self._client: Client = create_client(url, key)

    def listar_contatos(self, limite: int) -> list[Contato]:
        """Busca até `limite` contatos, ordenados por id. Ignora linhas sem nome/telefone."""
        logger.info("Buscando até %d contato(s) na tabela '%s'...", limite, self._table)

        response = (
            self._client.table(self._table)
            .select("id, nome, telefone")
            .order("id")
            .limit(limite)
            .execute()
        )

        registros = response.data or []
        contatos = []
        for registro in registros:
            contato = self._parse_registro(registro)
            if contato:
                contatos.append(contato)

        logger.info("%d contato(s) válido(s) encontrado(s).", len(contatos))
        return contatos

    @staticmethod
    def _parse_registro(registro: dict) -> Contato | None:
        nome = (registro.get("nome") or "").strip()
        telefone = (registro.get("telefone") or "").strip()
        registro_id = registro.get("id")

        if not nome or not telefone:
            logger.warning(
                "Registro id=%s ignorado: nome ou telefone ausente (nome=%r, telefone=%r).",
                registro_id, nome, telefone,
            )
            return None

        return Contato(id=str(registro_id), nome=nome, telefone=telefone)