import re

FEEDBACK_AR_DICT = {
    "Excellent ! Tu as bien decrit le role de l'ARN polymerase.":
        ".ممتاز ! لقد وصفت دور بوليميراز ARN بشكل جيد",
    "Excellent ! Tu as bien decrit le mecanisme de la replication de l'ADN.":
        ".ممتاز ! لقد وصفت آلية تضاعف ADN بشكل جيد",
    "Excellent ! Tu as bien decrit les etapes de la mitose.":
        ".ممتاز ! لقد وصفت مراحل الانقسام الخيطي بشكل جيد",
    "Excellent ! Tu as bien decrit le role des organites cellulaires.":
        ".ممتاز ! لقد وصفت دور العضيات الخلوية بشكل جيد",
    "Excellent ! Tu as bien decrit le fonctionnement du systeme nerveux.":
        ".ممتاز ! لقد وصفت عمل الجهاز العصبي بشكل جيد",
    "Excellent ! Tu maîtrises parfaitement ce concept.":
        "!ممتاز ! أنت تتقن هذا المفهوم تمامًا",
    "Bien ! Tu as compris les idees principales.":
        ".جيد ! لقد فهمت الأفكار الرئيسية",
    "Bien ! Tu as saisi les bases.":
        ".جيد ! لقد أمسكت بالأساسيات",
    "A revoir ! Revise les concepts suivants :":
        ":يراجع ! راجع المفاهيم التالية",
    "A revoir ! Quelques confusions dans ta reponse.":
        ".يراجع ! بعض الالتباسات في إجابتك",
    "Concepts manquants":
        "المفاهيم الناقصة",
    "Il manque des elements essentiels.":
        ".توجد عناصر أساسية مفقودة",
    "Tu as bien":
        "لقد وصفت بشكل جيد",
    "Tu maîtrises":
        "أنت تتقن",
    "Revois le cours":
        "راجع الدرس",
    "Revois la notion de":
        "راجع مفهوم",
    "Revois les concepts suivants":
        "راجع المفاهيم التالية",
    "Continue comme ca !":
        "!واصل هكذا",
    "Bon travail !":
        "!عمل جيد",
}

AR_PREFIXES = [
    (re.compile(r"^Excellent\s*!", re.IGNORECASE), "!ممتاز"),
    (re.compile(r"^Bien\s*!", re.IGNORECASE), "!جيد"),
    (re.compile(r"^A revoir\s*!", re.IGNORECASE), "!يراجع"),
    (re.compile(r"^Parfait\s*!", re.IGNORECASE), "!ممتاز"),
]

def translate_feedback(text_fr: str) -> str:
    if not text_fr:
        return text_fr

    # 1. Exact match — handles full known sentences
    if text_fr in FEEDBACK_AR_DICT:
        return FEEDBACK_AR_DICT[text_fr]

    result = text_fr

    # 2. Replace known phrases (longest first) on the original text
    for fr_phrase, ar_phrase in sorted(FEEDBACK_AR_DICT.items(), key=lambda x: -len(x[0])):
        result = result.replace(fr_phrase, ar_phrase)

    # 3. Replace prefixes via regex (e.g. "Excellent !" → "!ممتاز")
    for fr_pattern, ar_prefix in AR_PREFIXES:
        if fr_pattern.match(result):
            result = fr_pattern.sub(ar_prefix, result)
            break

    return result
