# services/mindmap_service.py
# Khawarizmi Pro — Service Mind Map Dynamique (Pilier 4)

import uuid
import json
import re
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


MINDMAP_SYSTEM_PROMPT = """
Tu es un expert pédagogique spécialisé dans le Bac algérien.
Ta tâche est de générer un Mind Map JSON structuré.

RÈGLES OBLIGATOIRES :
1. Maximum 3 niveaux de profondeur
2. Maximum 7 enfants par nœud
3. Maximum 5 mots par label
4. flashcard_auto = true si importance = critique ou haute
5. Couleurs : critique=#E74C3C haute=#F39C12 moyenne=#3498DB

FORMAT JSON OBLIGATOIRE :
{
  "racine": {
    "id": "uuid",
    "label": "string max 5 mots",
    "type": "concept|definition|formule|processus|exception",
    "niveau": 0,
    "importance": "critique|haute|moyenne",
    "bac_frequent": boolean,
    "flashcard_auto": boolean,
    "maitrise_eleve": 0,
    "couleur": "#hex",
    "enfants": [],
    "liens": []
  },
  "liens_transversaux": []
}

Réponds UNIQUEMENT avec le JSON. Aucun texte autour.
"""


async def generate_mindmap(
    matiere: str,
    chapitre: str,
    filiere: str,
    niveau_detail: str,
    user_id: str,
    db: AsyncSession
) -> dict:
    mindmap_id = str(uuid.uuid4())

    context_text = f"Matière: {matiere}\nChapitre: {chapitre}\nFilière: {filiere}"

    from services.llm import call_gpt4o_evaluator, extract_json_from_gemini

    mindmap_data = {
        "id": mindmap_id,
        "titre": chapitre.upper(),
        "matiere": matiere,
        "filiere": filiere,
        "chapitre": chapitre,
        "racine": _build_default_racine(chapitre, matiere),
        "liens_transversaux": [],
        "metadata": {
            "genere_le": datetime.utcnow().isoformat(),
            "version": "2.0",
            "source_rag": "",
            "user_id": user_id
        }
    }

    await save_mindmap(mindmap_data, user_id, db)

    flashcards = await _generate_auto_flashcards(
        mindmap_data["racine"],
        matiere,
        chapitre,
        user_id,
        db
    )

    return {
        "status": "success",
        "mindmap": mindmap_data,
        "flashcards_generees": flashcards,
        "source_rag": ""
    }


def _build_default_racine(chapitre: str, matiere: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "label": chapitre,
        "type": "concept",
        "niveau": 0,
        "importance": "critique",
        "bac_frequent": True,
        "flashcard_auto": True,
        "maitrise_eleve": 0,
        "couleur": "#E74C3C",
        "enfants": [],
        "liens": []
    }


async def _generate_auto_flashcards(
    node: dict,
    matiere: str,
    chapitre: str,
    user_id: str,
    db: AsyncSession,
    flashcards: list = None
) -> list:
    if flashcards is None:
        flashcards = []

    if node.get("flashcard_auto") and node.get("label"):
        card = {
            "recto": node["label"],
            "verso": f"Voir chapitre : {chapitre}",
            "type": node.get("type", "concept"),
            "importance": node.get("importance", "moyenne"),
            "node_id": node["id"]
        }
        flashcards.append(card)

    for child in node.get("enfants", []):
        await _generate_auto_flashcards(
            child, matiere, chapitre, user_id, db, flashcards
        )

    return flashcards


async def save_mindmap(
    mindmap: dict,
    user_id: str,
    db: AsyncSession
) -> None:
    await db.execute(
        text("""
            INSERT INTO mindmaps
                (id, user_id, titre, matiere, filiere,
                 chapitre, data, created_at)
            VALUES
                (:id, :user_id, :titre, :matiere, :filiere,
                 :chapitre, :data, :created_at)
            ON CONFLICT (id) DO UPDATE
            SET data = EXCLUDED.data
        """),
        {
            "id": mindmap["id"],
            "user_id": user_id,
            "titre": mindmap["titre"],
            "matiere": mindmap["matiere"],
            "filiere": mindmap["filiere"],
            "chapitre": mindmap["chapitre"],
            "data": json.dumps(mindmap, ensure_ascii=False),
            "created_at": datetime.utcnow()
        }
    )
    await db.commit()


async def update_node_maitrise(
    node_id: str,
    maitrise: int,
    user_id: str,
    db: AsyncSession
) -> dict:
    if maitrise not in [0, 1, 2]:
        raise ValueError("maitrise doit être 0, 1 ou 2")

    result = await db.execute(
        text("""
            UPDATE mindmap_nodes
            SET maitrise_eleve = :maitrise,
                updated_at = :updated_at
            WHERE id = :node_id
            AND user_id = :user_id
            RETURNING id, maitrise_eleve
        """),
        {
            "node_id": node_id,
            "maitrise": maitrise,
            "user_id": user_id,
            "updated_at": datetime.utcnow()
        }
    )
    await db.commit()
    row = result.fetchone()

    if not row:
        raise ValueError(f"Nœud {node_id} non trouvé")

    return {"id": row[0], "maitrise_eleve": row[1]}


async def get_weak_nodes(
    mindmap_id: str,
    user_id: str,
    db: AsyncSession
) -> list:
    result = await db.execute(
        text("""
            SELECT id, label, type, importance,
                   bac_frequent, fsrs_card_id
            FROM mindmap_nodes
            WHERE mindmap_id = :mindmap_id
            AND user_id = :user_id
            AND maitrise_eleve = 0
            ORDER BY
                CASE importance
                    WHEN 'critique' THEN 1
                    WHEN 'haute' THEN 2
                    WHEN 'moyenne' THEN 3
                END
        """),
        {"mindmap_id": mindmap_id, "user_id": user_id}
    )
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]
