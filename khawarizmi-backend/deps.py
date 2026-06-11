"""
deps.py — Dépendances partagées FastAPI (Khawarizmi)
-----------------------------------------------------
Ce module existe UNIQUEMENT pour casser le cycle d'import circulaire :
    main.py → routes/*.py → main.py   (circular → crash)

Il importe lazily depuis main.state et main.get_settings en utilisant
des fonctions qui ne sont appelées qu'au moment de la requête, pas au
chargement du module.

Règle : ne jamais importer routes.* ici.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any, Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from jose import JWTError, jwt


# ── Helpers lazy (évitent l'import top-level de main) ────────────────────────

def _get_state():
    """Retourne l'objet AppState de main sans l'importer au chargement."""
    from main import state  # noqa: PLC0415 — import tardif intentionnel
    return state


def _get_cfg():
    from main import get_settings  # noqa: PLC0415
    return get_settings()


# ── DB ────────────────────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    """Injecte une session DB dans les routes."""
    s = _get_state()
    if not s.db_session:
        raise HTTPException(503, "Base de données indisponible")
    async with s.db_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Services ──────────────────────────────────────────────────────────────────

def get_tutor():
    s = _get_state()
    if not s.tutor:
        raise HTTPException(503, "Moteur pédagogique non initialisé")
    return s.tutor


def get_scheduler():
    s = _get_state()
    if not s.scheduler:
        raise HTTPException(503, "Scheduler FSRS non initialisé")
    return s.scheduler


def get_openai():
    s = _get_state()
    if not s.openai:
        raise HTTPException(503, "Service IA non configuré — clé API manquante")
    return s.openai


def get_settings():
    return _get_cfg()


# ── Auth ──────────────────────────────────────────────────────────────────────

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Vérifie le JWT et retourne l'utilisateur courant."""
    cfg = _get_cfg()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, cfg.secret_key, algorithms=[cfg.algorithm])
        user_id: int = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        text("SELECT id, email, prenom, plan FROM users WHERE id = :id"),
        {"id": user_id},
    )
    user = result.fetchone()
    if not user:
        raise credentials_exception

    return {"id": user[0], "email": user[1], "prenom": user[2], "plan": user[3]}
