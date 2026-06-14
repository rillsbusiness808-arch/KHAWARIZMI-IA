import json
import logging
from datetime import datetime, timezone
from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from deps import get_current_user, get_db, get_scheduler
from schemas.flashcard import DrillRequest, ScheduleRequest
from fsrs import Card

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


def _get_state():
    from main import state
    return state


@router.post("/api/drill/session", tags=["Drill"])
async def generer_session_drill(
    body:         DrillRequest,
    current_user: Dict          = Depends(get_current_user),
    db:           AsyncSession  = Depends(get_db),
):
    s = _get_state()
    session = await s.interleaving.generer_session(
        user_id      = current_user["id"],
        db           = db,
        matiere      = body.matiere,
        nb_questions = body.nb_questions,
    )

    if current_user["plan"] == "free":
        session["questions"] = session["questions"][:5]
        session["nb_questions"] = len(session["questions"])
        session["quota_atteint"] = len(session["questions"]) == 5

    logger.info(
        f"Drill : user={current_user['id']} "
        f"matiere={body.matiere} "
        f"questions={session['nb_questions']}"
    )

    return session


@router.post("/api/drill/result", tags=["Drill"])
async def soumettre_resultat_drill(
    body:         ScheduleRequest,
    current_user: Dict           = Depends(get_current_user),
    db:           AsyncSession   = Depends(get_db),
):
    scheduler = get_scheduler()

    fsrs_state = body.fsrs_state or {}
    card = Card()

    result = scheduler.calculer_prochain_intervalle(card, body.score_percent)
    new_card = result["card"]

    fsrs_json = json.dumps({
        "stability":      new_card.stability,
        "difficulty":     new_card.difficulty,
        "scheduled_days": new_card.scheduled_days,
        "reps":           new_card.reps,
        "lapses":         new_card.lapses,
        "state":          str(new_card.state),
        "last_review":    datetime.now(timezone.utc).isoformat(),
    })

    await db.execute(
        text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, prochaine_revision,
                 interval_jours, difficulty, stability, fsrs_state)
            VALUES
                (:user_id, :mc_id, :next_rev,
                 :interval, :difficulty, :stability, :fsrs_state::jsonb)
            ON CONFLICT (user_id, micro_concept_id)
            DO UPDATE SET
                prochaine_revision = EXCLUDED.prochaine_revision,
                interval_jours     = EXCLUDED.interval_jours,
                difficulty         = EXCLUDED.difficulty,
                stability          = EXCLUDED.stability,
                fsrs_state         = EXCLUDED.fsrs_state,
                updated_at         = NOW()
        """),
        {
            "user_id":    current_user["id"],
            "mc_id":      body.micro_concept_id,
            "next_rev":   result["prochaine_revision"],
            "interval":   result["interval_jours"],
            "difficulty": result["difficulty"],
            "stability":  result["stability"],
            "fsrs_state": fsrs_json,
        }
    )

    logger.info(
        f"FSRS update : user={current_user['id']} "
        f"mc={body.micro_concept_id} "
        f"score={body.score_percent}% "
        f"→ {result['interval_jours']}j"
    )

    return {
        "prochaine_revision": result["prochaine_revision"].isoformat(),
        "interval_jours":     result["interval_jours"],
        "retrievability":     result["retrievability"],
        "rating":             result["rating"],
    }
