import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


STOP_WORDS = {
    "а",
    "без",
    "бы",
    "в",
    "вам",
    "вас",
    "ваш",
    "ваша",
    "ваше",
    "вы",
    "где",
    "да",
    "для",
    "до",
    "его",
    "если",
    "есть",
    "и",
    "из",
    "или",
    "как",
    "какие",
    "какой",
    "к",
    "ли",
    "мы",
    "на",
    "надо",
    "не",
    "о",
    "об",
    "от",
    "по",
    "под",
    "при",
    "про",
    "с",
    "со",
    "так",
    "у",
    "что",
    "это",
}


@dataclass(frozen=True)
class FaqItem:
    question: str
    answer: str


@dataclass(frozen=True)
class FaqMatch:
    item: FaqItem
    score: int


def _tokens(text: str) -> set[str]:
    normalized = text.lower().replace("ё", "е")
    words = re.findall(r"[a-zа-я0-9]+", normalized)
    return {word for word in words if len(word) >= 3 and word not in STOP_WORDS}


@lru_cache
def load_faq_items() -> tuple[FaqItem, ...]:
    path = Path(__file__).with_name("data") / "faq_answers.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return tuple(FaqItem(question=item["question"], answer=item["answer"]) for item in payload)


def find_faq_matches(query: str, limit: int = 2) -> list[FaqMatch]:
    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    matches: list[FaqMatch] = []
    for item in load_faq_items():
        question_tokens = _tokens(item.question)
        answer_tokens = _tokens(item.answer)
        question_overlap = query_tokens & question_tokens
        answer_overlap = query_tokens & answer_tokens
        score = len(question_overlap) * 4 + len(answer_overlap)
        if score:
            matches.append(FaqMatch(item=item, score=score))

    matches.sort(key=lambda match: match.score, reverse=True)
    if not matches:
        return []

    minimum_score = max(2, matches[0].score // 3)
    return [match for match in matches if match.score >= minimum_score][:limit]
