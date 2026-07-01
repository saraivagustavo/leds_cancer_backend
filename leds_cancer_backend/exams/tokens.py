"""
Utilitários HMAC para geração e validação de tokens de acesso a imagens de exames.

Fluxo:
  1. Frontend (usuário autenticado) chama POST /api/exams/{id}/image-token/
     → recebe { token, expires_at }
  2. Serviço externo chama GET /api/exams/{id}/image/?token=<valor>&expires=<ts>
     → recebe o arquivo de imagem diretamente (FileResponse)

O token é HMAC-SHA256(IMAGE_TOKEN_SECRET, "{exam_id}:{expires_ts}").
Stateless — não é armazenado no banco.
"""

import hashlib
import hmac
import time

from django.conf import settings

# Tempo de vida padrão do token em segundos (sobrescrito por IMAGE_TOKEN_TTL_SECONDS no settings)
_DEFAULT_TTL = 900  # 15 minutos


def _secret() -> bytes:
    """Retorna o segredo de assinatura dos tokens de imagem."""
    key: str = getattr(settings, "IMAGE_TOKEN_SECRET", settings.SECRET_KEY)
    return key.encode()


def _make_token(exam_id: int, expires_ts: int) -> str:
    """Produz o HMAC-SHA256 para o par (exam_id, expires_ts)."""
    message = f"{exam_id}:{expires_ts}".encode()
    return hmac.new(_secret(), message, hashlib.sha256).hexdigest()


def generate_token(exam_id: int) -> tuple[str, int]:
    """
    Gera um token de acesso temporário para a imagem do exame.

    Retorna:
        (token, expires_ts)
        - token      — hex HMAC-SHA256
        - expires_ts — Unix timestamp de expiração
    """
    ttl: int = getattr(settings, "IMAGE_TOKEN_TTL_SECONDS", _DEFAULT_TTL)
    expires_ts = int(time.time()) + ttl
    return _make_token(exam_id, expires_ts), expires_ts


def verify_token(exam_id: int, token: str, expires_ts: int) -> bool:
    """
    Verifica autenticidade e validade do token.

    - Usa hmac.compare_digest para evitar timing attacks.
    - Rejeita tokens já expirados antes de fazer a comparação.
    """
    if int(time.time()) > expires_ts:
        return False
    expected = _make_token(exam_id, expires_ts)
    return hmac.compare_digest(expected, token)
