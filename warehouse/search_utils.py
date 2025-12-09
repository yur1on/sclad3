import re
from typing import Optional, Tuple

_ALNUM_TOKENS_RE = re.compile(r"[A-Za-z0-9]+")
_DIGIT_RE = re.compile(r"\d")


def normalize_compact(text: str) -> str:
    """
    Для сравнения "без мусора": убираем пробелы и дефисы, приводим к lower.
    """
    t = (text or "").strip().lower()
    t = re.sub(r"[\s\-]+", "", t)
    return t


def tokenize_alnum(text: str):
    return _ALNUM_TOKENS_RE.findall(text or "")


def is_modelish_token(tok: str) -> bool:
    tok = (tok or "").strip()
    return len(tok) >= 3 and bool(_DIGIT_RE.search(tok))


def note_regex_from_text(text: str) -> Optional[str]:
    """
    Ищем модельные токены в note как отдельные слова (PostgreSQL: \m...\M).
    a40 НЕ матчится с a401.
    """
    tokens = [t for t in tokenize_alnum(text) if is_modelish_token(t)]
    if not tokens:
        return None
    escaped = [re.escape(t) for t in tokens]
    return r"\m(?:%s)\M" % "|".join(escaped)


def split_search_q(q: str, brand_in: str = "", model_in: str = "") -> Tuple[str, str, bool, str, str]:
    """
    Разбор q:
    - 1 слово => single_term (модель/код ИЛИ бренд)
    - несколько => первое слово бренд (если не похоже на модель), остальное модель
    - если q пустой, но есть brand/model из GET — собираем q из них (совместимость)
    """
    q = (q or "").strip()
    brand_in = (brand_in or "").strip()
    model_in = (model_in or "").strip()

    brand = ""
    model = ""
    single_term = False
    term = ""

    if q:
        parts = q.split()
        if len(parts) == 1:
            single_term = True
            term = parts[0]
            model = term
        else:
            first = parts[0]
            # если первый токен похож на модель (есть цифры) — бренда нет
            if _DIGIT_RE.search(first):
                model = q
            else:
                brand = first
                model = " ".join(parts[1:])
    else:
        brand = brand_in
        model = model_in
        if brand and model:
            q = f"{brand} {model}"
        elif brand:
            q = brand
        elif model:
            q = model

    return brand, model, single_term, term, q
