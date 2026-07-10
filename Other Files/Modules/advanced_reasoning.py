"""High-value deterministic reasoning tools for Pocket AI.

This module improves small-model answers without pretending that retrieval or
prompting changes the parameter count of the underlying language model. It uses
only Python's standard library and is designed for low-memory Android devices.
"""
from __future__ import annotations

import ast
import math
import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

MODULE_VERSION = 2

_WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_NUMBER_RE = re.compile(r"(?<![\w.])-?\d+(?:[.,]\d+)?(?:e[+-]?\d+)?", re.I)

_STOP_EN = {
    "a", "an", "the", "and", "or", "but", "of", "to", "for", "in", "on", "at", "by", "with",
    "from", "as", "is", "are", "was", "were", "be", "been", "being", "do", "does", "did", "can",
    "could", "would", "should", "will", "may", "might", "what", "who", "which", "when", "where",
    "why", "how", "tell", "me", "please", "about", "explain", "describe", "give", "show", "this",
    "that", "these", "those", "between", "versus", "vs", "difference", "compare",
}
_STOP_EL = {
    "ο", "η", "το", "οι", "τα", "του", "της", "των", "σε", "με", "για", "απο", "από", "και",
    "ή", "αλλα", "αλλά", "ειναι", "είναι", "ηταν", "ήταν", "να", "θα", "που", "τι", "ποιος",
    "ποια", "ποιο", "ποτε", "πότε", "που", "πού", "γιατι", "γιατί", "πως", "πώς", "πες", "μου",
    "εξηγησε", "εξήγησε", "δωσε", "δώσε", "δειξε", "δείξε", "μεταξυ", "μεταξύ", "εναντιον",
    "σύγκρινε", "συγκρινε", "διαφορα", "διαφορά", "διαφορές",
}

_SOURCE_PRIORS = {
    "common": 1.00,
    "tool": 1.00,
    "school": 0.96,
    "universal": 0.94,
    "specialist": 0.90,
    "encyclopedia": 0.87,
    "qa": 0.84,
    "document": 0.78,
    "lexical": 0.76,
    "memory": 0.74,
    "local": 0.70,
}


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", str(text).casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^0-9a-zα-ω+#._/%=<>*^-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _tokens(text: str, language: str = "en", keep_stop: bool = False) -> list[str]:
    stop = _STOP_EL if language == "el" else _STOP_EN
    values = [token for token in _WORD_RE.findall(normalize(text)) if len(token) >= 2]
    return values if keep_stop else [token for token in values if token not in stop]


def _split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", str(text)).strip()
    if not cleaned:
        return []
    values = [item.strip(" -\t") for item in _SENTENCE_RE.split(cleaned) if item.strip()]
    if len(values) == 1 and len(cleaned) > 460:
        words = cleaned.split()
        values = [" ".join(words[index:index + 52]) for index in range(0, len(words), 52)]
    return values


# ---------------------------------------------------------------------------
# Safe deterministic tools
# ---------------------------------------------------------------------------

_ALLOWED_BINARY = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}
_ALLOWED_UNARY = {ast.UAdd: lambda value: value, ast.USub: lambda value: -value}
_ALLOWED_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
}
_ALLOWED_CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


def _safe_eval(expression: str) -> float:
    if len(expression) > 240:
        raise ValueError("expression is too long")
    expression = expression.replace("^", "**").replace(",", ".")
    tree = ast.parse(expression, mode="eval")

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            value = float(node.value)
            if not math.isfinite(value):
                raise ValueError("non-finite number")
            return value
        if isinstance(node, ast.Name) and node.id in _ALLOWED_CONSTANTS:
            return float(_ALLOWED_CONSTANTS[node.id])
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 12:
                raise ValueError("exponent is too large")
            value = float(_ALLOWED_BINARY[type(node.op)](left, right))
            if not math.isfinite(value) or abs(value) > 1e100:
                raise ValueError("result is outside the safe range")
            return value
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
            return float(_ALLOWED_UNARY[type(node.op)](visit(node.operand)))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCTIONS:
            if node.keywords or len(node.args) > 2:
                raise ValueError("unsupported function arguments")
            args = [visit(arg) for arg in node.args]
            value = float(_ALLOWED_FUNCTIONS[node.func.id](*args))
            if not math.isfinite(value):
                raise ValueError("non-finite result")
            return value
        raise ValueError("unsupported expression")

    return visit(tree)


def _format_number(value: float) -> str:
    if abs(value - round(value)) < 1e-12:
        return str(int(round(value)))
    return f"{value:.12g}"


def _parse_number_list(text: str) -> list[float]:
    values = []
    for token in re.findall(r"-?\d+(?:[.,]\d+)?", text):
        try:
            values.append(float(token.replace(",", ".")))
        except ValueError:
            continue
    return values


def _linear_equation(text: str) -> tuple[float, float] | None:
    """Solve a limited but useful ax+b=c equation."""
    compact = normalize(text).replace(" ", "")
    compact = compact.replace("·", "*")
    match = re.search(r"(?:solve|λυσε)?([+-]?(?:\d+(?:\.\d+)?)?)\*?x([+-]\d+(?:\.\d+)?)?=([+-]?\d+(?:\.\d+)?)", compact)
    if not match:
        return None
    a_raw, b_raw, c_raw = match.groups()
    if a_raw in {"", "+", None}:
        a = 1.0
    elif a_raw == "-":
        a = -1.0
    else:
        a = float(a_raw)
    b = float(b_raw or 0.0)
    c = float(c_raw)
    if abs(a) < 1e-15:
        raise ValueError("the equation has no unique solution")
    return (c - b) / a, a


def _quadratic_coefficients(text: str) -> tuple[float, float, float] | None:
    compact = normalize(text).replace(" ", "").replace("²", "^2")
    compact = re.sub(r"^(?:solve|equation|λυσε|εξισωση)+", "", compact)
    if "x^2" not in compact or "=" not in compact:
        return None
    left, right = compact.split("=", 1)
    try:
        right_value = float(right)
    except ValueError:
        return None
    left = left.replace("-", "+-")
    terms = [term for term in left.split("+") if term]
    a = b = c = 0.0
    for term in terms:
        if "x^2" in term:
            raw = term.replace("*", "").replace("x^2", "")
            a += -1.0 if raw == "-" else (1.0 if raw in {"", "+"} else float(raw))
        elif "x" in term:
            raw = term.replace("*", "").replace("x", "")
            b += -1.0 if raw == "-" else (1.0 if raw in {"", "+"} else float(raw))
        else:
            c += float(term)
    c -= right_value
    if abs(a) < 1e-15:
        return None
    return a, b, c


_UNIT_ALIASES = {
    "mm": "mm", "millimeter": "mm", "millimeters": "mm", "χιλιοστο": "mm", "χιλιοστα": "mm",
    "cm": "cm", "centimeter": "cm", "centimeters": "cm", "εκατοστο": "cm", "εκατοστα": "cm",
    "m": "m", "meter": "m", "meters": "m", "metre": "m", "metres": "m", "μετρο": "m", "μετρα": "m",
    "km": "km", "kilometer": "km", "kilometers": "km", "kilometre": "km", "kilometres": "km", "χιλιομετρο": "km", "χιλιομετρα": "km",
    "in": "in", "inch": "in", "inches": "in", "ιντσα": "in", "ιντσες": "in",
    "ft": "ft", "foot": "ft", "feet": "ft", "ποδι": "ft", "ποδια": "ft",
    "yd": "yd", "yard": "yd", "yards": "yd", "γιαρδα": "yd", "γιαρδες": "yd",
    "mi": "mi", "mile": "mi", "miles": "mi", "μιλι": "mi", "μιλια": "mi",
    "mg": "mg", "milligram": "mg", "milligrams": "mg",
    "g": "g", "gram": "g", "grams": "g", "γραμμαριο": "g", "γραμμαρια": "g",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg", "κιλο": "kg", "κιλα": "kg",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb", "λιβρα": "lb", "λιβρες": "lb",
    "ml": "ml", "milliliter": "ml", "milliliters": "ml", "millilitre": "ml", "millilitres": "ml",
    "l": "l", "liter": "l", "liters": "l", "litre": "l", "litres": "l", "λιτρο": "l", "λιτρα": "l",
}
_UNIT_FACTORS = {
    "mm": ("length", 0.001), "cm": ("length", 0.01), "m": ("length", 1.0), "km": ("length", 1000.0),
    "in": ("length", 0.0254), "ft": ("length", 0.3048), "yd": ("length", 0.9144), "mi": ("length", 1609.344),
    "mg": ("mass", 0.000001), "g": ("mass", 0.001), "kg": ("mass", 1.0),
    "oz": ("mass", 0.028349523125), "lb": ("mass", 0.45359237),
    "ml": ("volume", 0.001), "l": ("volume", 1.0),
}
_UNIT_LABELS = {"mm":"mm","cm":"cm","m":"m","km":"km","in":"in","ft":"ft","yd":"yd","mi":"mi","mg":"mg","g":"g","kg":"kg","oz":"oz","lb":"lb","ml":"mL","l":"L"}


def _unit_conversion(text: str, language: str) -> dict | None:
    n = normalize(text)
    # Temperature is affine rather than multiplicative.
    temp = re.search(r"(-?\d+(?:[.,]\d+)?)\s*(c|celsius|f|fahrenheit|k|kelvin)\s+(?:to|in|σε)\s*(c|celsius|f|fahrenheit|k|kelvin)", n)
    if temp and any(cue in n for cue in ("convert", "conversion", "μετατροπη", "μετατρεψε", "ποσο ειναι")):
        value = float(temp.group(1).replace(",", ".")); src=temp.group(2)[0]; dst=temp.group(3)[0]
        kelvin = value + 273.15 if src == "c" else ((value - 32.0) * 5.0 / 9.0 + 273.15 if src == "f" else value)
        result = kelvin - 273.15 if dst == "c" else ((kelvin - 273.15) * 9.0 / 5.0 + 32.0 if dst == "f" else kelvin)
        rendered=_format_number(result); units={"c":"°C","f":"°F","k":"K"}
        response=f"{_format_number(value)} {units[src]} = {rendered} {units[dst]}."
        return {"response":response,"route":"exact_temperature_conversion","confidence":1.0,"evidence":response}
    match = re.search(r"(-?\d+(?:[.,]\d+)?)\s*([a-zα-ω]+)\s+(?:to|in|σε)\s+([a-zα-ω]+)", n)
    if not match or not any(cue in n for cue in ("convert", "conversion", "μετατροπη", "μετατρεψε", "ποσο ειναι")):
        return None
    value=float(match.group(1).replace(",", ".")); src=_UNIT_ALIASES.get(match.group(2)); dst=_UNIT_ALIASES.get(match.group(3))
    if not src or not dst or _UNIT_FACTORS[src][0] != _UNIT_FACTORS[dst][0]:
        return None
    result=value * _UNIT_FACTORS[src][1] / _UNIT_FACTORS[dst][1]
    response=f"{_format_number(value)} {_UNIT_LABELS[src]} = {_format_number(result)} {_UNIT_LABELS[dst]}."
    return {"response":response,"route":"exact_unit_conversion","confidence":1.0,"evidence":response}


def solve_tool_query(text: str, language: str = "en") -> dict | None:
    """Return an exact answer for tool-solvable questions, otherwise ``None``."""
    raw = str(text).strip()
    n = normalize(raw)
    if not raw:
        return None

    conversion = _unit_conversion(raw, language)
    if conversion:
        return conversion

    # Character counting catches a common failure mode of tiny LLMs.
    match = re.search(
        r"(?:how many|count)\s+(?:times\s+)?(?:the\s+)?(?:letter|character)?\s*['\"]?(.{1})['\"]?\s+(?:are\s+)?(?:in|inside)\s+['\"]?([^'\"?]+)|"
        r"(?:ποσα|πόσα)\s+(?:γραμματα|γράμματα|φορες|φορές)?\s*['\"]?(.{1})['\"]?\s+(?:εχει|έχει|υπαρχουν|υπάρχουν)\s+(?:στη|στην|στο)\s+['\"]?([^'\"?]+)",
        raw, flags=re.I,
    )
    if match:
        letter = (match.group(1) or match.group(3) or "").casefold()
        word = (match.group(2) or match.group(4) or "").strip().rstrip("?.!")
        count = word.casefold().count(letter)
        response = (
            f"The letter “{letter}” appears {count} time{'s' if count != 1 else ''} in “{word}”."
            if language != "el" else
            f"Το γράμμα «{letter}» εμφανίζεται {count} φορά{'ές' if count != 1 else ''} στη λέξη «{word}»."
        )
        return {"response": response, "route": "exact_character_count", "confidence": 1.0, "evidence": response}

    # Percentage of a number.
    match = re.search(r"(-?\d+(?:[.,]\d+)?)\s*%\s*(?:of|του|της|απο|από)\s*(-?\d+(?:[.,]\d+)?)", n)
    if match:
        percentage = float(match.group(1).replace(",", "."))
        base = float(match.group(2).replace(",", "."))
        result = base * percentage / 100.0
        rendered = _format_number(result)
        response = (
            f"{_format_number(percentage)}% of {_format_number(base)} is {rendered}. Calculation: {_format_number(base)} × {_format_number(percentage)} ÷ 100 = {rendered}."
            if language != "el" else
            f"Το {_format_number(percentage)}% του {_format_number(base)} είναι {rendered}. Υπολογισμός: {_format_number(base)} × {_format_number(percentage)} ÷ 100 = {rendered}."
        )
        return {"response": response, "route": "exact_percentage", "confidence": 1.0, "evidence": response}

    # Increase/decrease by a percentage.
    match = re.search(r"(?:increase|raise|αυξησε|αύξησε)\s+(-?\d+(?:[.,]\d+)?)\s+(?:by|κατα|κατά)\s+(-?\d+(?:[.,]\d+)?)\s*%", n)
    direction = 1.0
    if not match:
        match = re.search(r"(?:decrease|reduce|μειωσε|μείωσε)\s+(-?\d+(?:[.,]\d+)?)\s+(?:by|κατα|κατά)\s+(-?\d+(?:[.,]\d+)?)\s*%", n)
        direction = -1.0
    if match:
        base, percentage = (float(value.replace(",", ".")) for value in match.groups())
        delta = base * percentage / 100.0
        result = base + direction * delta
        response = (
            f"Result: {_format_number(result)}. The change is {_format_number(abs(delta))}."
            if language != "el" else
            f"Αποτέλεσμα: {_format_number(result)}. Η μεταβολή είναι {_format_number(abs(delta))}."
        )
        return {"response": response, "route": "exact_percent_change", "confidence": 1.0, "evidence": response}

    # Linear and quadratic equations.
    if any(cue in n for cue in ("solve", "equation", "λυσε", "εξισωση", "x=")) and "=" in n:
        coefficients = _quadratic_coefficients(n)
        if coefficients:
            a, b, c = coefficients
            discriminant = b * b - 4 * a * c
            if discriminant < -1e-12:
                response = (
                    f"The equation has no real roots because the discriminant is {_format_number(discriminant)}."
                    if language != "el" else
                    f"Η εξίσωση δεν έχει πραγματικές ρίζες, επειδή η διακρίνουσα είναι {_format_number(discriminant)}."
                )
            elif abs(discriminant) <= 1e-12:
                root = -b / (2 * a)
                response = (
                    f"The equation has one repeated root: x = {_format_number(root)}."
                    if language != "el" else
                    f"Η εξίσωση έχει μία διπλή ρίζα: x = {_format_number(root)}."
                )
            else:
                root = math.sqrt(discriminant)
                x1, x2 = (-b + root) / (2 * a), (-b - root) / (2 * a)
                response = (
                    f"The roots are x₁ = {_format_number(x1)} and x₂ = {_format_number(x2)}. The discriminant is {_format_number(discriminant)}."
                    if language != "el" else
                    f"Οι ρίζες είναι x₁ = {_format_number(x1)} και x₂ = {_format_number(x2)}. Η διακρίνουσα είναι {_format_number(discriminant)}."
                )
            return {"response": response, "route": "exact_quadratic", "confidence": 1.0, "evidence": response}
        try:
            linear = _linear_equation(n)
        except ValueError as error:
            response = str(error) if language != "el" else "Η εξίσωση δεν έχει μοναδική λύση."
            return {"response": response, "route": "exact_linear_equation", "confidence": 1.0, "evidence": response}
        if linear:
            x, _ = linear
            response = f"x = {_format_number(x)}." if language != "el" else f"x = {_format_number(x)}."
            return {"response": response, "route": "exact_linear_equation", "confidence": 1.0, "evidence": response}

    # GCD / LCM / factorial / primality.
    match = re.search(r"(?:gcd|greatest common divisor|mcd|μεγιστος κοινος διαιρετης|μεγιστο κοινο διαιρετη)\D+(-?\d+)\D+(-?\d+)", n)
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        result = math.gcd(a, b)
        response = f"GCD({a}, {b}) = {result}." if language != "el" else f"ΜΚΔ({a}, {b}) = {result}."
        return {"response": response, "route": "exact_gcd", "confidence": 1.0, "evidence": response}
    match = re.search(r"(?:lcm|least common multiple|ελαχιστο κοινο πολλαπλασιο|εκπ)\D+(-?\d+)\D+(-?\d+)", n)
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        result = abs(a * b) // math.gcd(a, b) if a and b else 0
        response = f"LCM({a}, {b}) = {result}." if language != "el" else f"ΕΚΠ({a}, {b}) = {result}."
        return {"response": response, "route": "exact_lcm", "confidence": 1.0, "evidence": response}
    match = re.search(r"(?:factorial|παραγοντικο)\s*(?:of|του)?\s*(\d{1,4})", n)
    if match:
        value = int(match.group(1))
        if value > 500:
            return None
        result = math.factorial(value)
        response = f"{value}! = {result}."
        return {"response": response, "route": "exact_factorial", "confidence": 1.0, "evidence": response}
    match = re.search(r"(?:is|ειναι)\s+(\d{1,15})\s+(?:a\s+)?(?:prime|πρωτος αριθμος|πρώτος αριθμός)", n)
    if match:
        value = int(match.group(1))
        prime = value >= 2 and all(value % divisor for divisor in range(2, int(math.isqrt(value)) + 1))
        response = (
            f"{value} is {'prime' if prime else 'not prime'}."
            if language != "el" else
            f"Ο αριθμός {value} {'είναι πρώτος' if prime else 'δεν είναι πρώτος'}."
        )
        return {"response": response, "route": "exact_prime_test", "confidence": 1.0, "evidence": response}

    # Descriptive statistics when explicitly requested.
    if any(cue in n for cue in ("mean", "average", "median", "mode", "range", "μεσος ορος", "διαμεσος", "επικρατουσα", "ευρος")):
        values = _parse_number_list(raw)
        if 2 <= len(values) <= 500:
            mean = statistics.fmean(values)
            median = statistics.median(values)
            modes = statistics.multimode(values)
            value_range = max(values) - min(values)
            mode_text = ", ".join(_format_number(value) for value in modes[:6])
            if language != "el":
                response = f"Mean: {_format_number(mean)}; median: {_format_number(median)}; mode: {mode_text}; range: {_format_number(value_range)}."
            else:
                response = f"Μέσος όρος: {_format_number(mean)}· διάμεσος: {_format_number(median)}· επικρατούσα τιμή: {mode_text}· εύρος: {_format_number(value_range)}."
            return {"response": response, "route": "exact_statistics", "confidence": 1.0, "evidence": response}

    # Binary / hexadecimal conversions.
    match = re.search(r"(?:convert\s+)?(0b[01]+|0x[0-9a-f]+|\d+)\s+(?:from\s+)?(?:binary|hex(?:adecimal)?|decimal)?\s*(?:to|into|σε)\s*(binary|hex(?:adecimal)?|decimal|δυαδικο|δεκαεξαδικο|δεκαδικο)", n)
    if match:
        raw_value, target = match.groups()
        base = 2 if raw_value.startswith("0b") else (16 if raw_value.startswith("0x") else 10)
        value = int(raw_value, base)
        if target in {"binary", "δυαδικο"}:
            rendered = bin(value)
        elif target in {"hex", "hexadecimal", "δεκαεξαδικο"}:
            rendered = hex(value)
        else:
            rendered = str(value)
        response = f"{raw_value} = {rendered}."
        return {"response": response, "route": "exact_base_conversion", "confidence": 1.0, "evidence": response}

    # Natural arithmetic requests. Restrict aggressively to avoid interpreting prose.
    arithmetic = None
    prefix_patterns = (
        r"^(?:what is|calculate|compute|result of|ποσο κανει|πόσο κάνει|υπολογισε|υπολόγισε)\s+(.+?)[?]?$",
        r"^=\s*(.+)$",
    )
    for pattern in prefix_patterns:
        match = re.match(pattern, n)
        if match:
            arithmetic = match.group(1)
            break
    if arithmetic and re.fullmatch(r"[0-9eEpi.tauabsroundsqrtincoslogxfloorceil+*/%()\s,._^-]+", arithmetic):
        try:
            value = _safe_eval(arithmetic)
        except (ValueError, ZeroDivisionError, OverflowError, SyntaxError):
            return None
        rendered = _format_number(value)
        response = f"Result: {rendered}." if language != "el" else f"Αποτέλεσμα: {rendered}."
        return {"response": response, "route": "exact_arithmetic", "confidence": 1.0, "evidence": response}

    return None


# ---------------------------------------------------------------------------
# Query planning and evidence reasoning
# ---------------------------------------------------------------------------


def _comparison_entities(text: str, language: str = "en") -> list[str]:
    raw = re.sub(r"\s+", " ", str(text)).strip(" ?.!\t")
    patterns = [
        r"(?:difference(?:s)? between|compare)\s+(.+?)\s+(?:and|with)\s+(.+)$",
        r"(.+?)\s+(?:versus|vs\.?|v\.)\s+(.+)$",
        r"(?:διαφορα|διαφορές|διαφορά)\s+(?:μεταξυ|μεταξύ)\s+(.+?)\s+και\s+(.+)$",
        r"(?:συγκρινε|σύγκρινε)\s+(.+?)\s+(?:με|και)\s+(.+)$",
        r"(.+?)\s+(?:εναντιον|έναντι)\s+(.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, flags=re.I)
        if not match:
            continue
        entities = []
        for value in match.groups():
            value = re.sub(r"^(?:the|το|την|τη|τον)\s+", "", value.strip(), flags=re.I)
            value = re.sub(r"\s+(?:and tell me.*|και πες μου.*)$", "", value, flags=re.I)
            if 1 <= len(value) <= 90:
                entities.append(value)
        if len(entities) == 2:
            return entities
    return []


def _extract_constraints(text: str, language: str = "en") -> list[str]:
    normalized = normalize(text)
    cues = [
        "under", "less than", "at most", "no more than", "without", "must", "only", "at least",
        "below", "older", "newer", "faster", "offline", "free", "safe", "private",
        "κατω απο", "λιγοτερο απο", "το πολυ", "χωρις", "πρεπει", "μονο", "τουλαχιστον",
        "δωρεαν", "ασφαλες", "ιδιωτικο", "offline",
    ]
    constraints = []
    for cue in cues:
        pos = normalized.find(normalize(cue))
        if pos >= 0:
            fragment = normalized[pos:pos + 110].strip()
            if fragment and fragment not in constraints:
                constraints.append(fragment)
    return constraints[:6]


def _split_subquestions(text: str, language: str = "en") -> list[str]:
    raw = re.sub(r"\s+", " ", str(text)).strip()
    if not raw:
        return []
    parts = [part.strip(" ,;?.") for part in re.split(r"[?;]+|\b(?:also|then|and also|επισης|επίσης|και μετα|και μετά)\b", raw, flags=re.I) if part.strip(" ,;?.")]
    unique = []
    for part in parts:
        if len(part.split()) < 2:
            continue
        key = normalize(part)
        if key and key not in {normalize(item) for item in unique}:
            unique.append(part)
    return unique[:5] or [raw]


def plan_query(text: str, language: str = "en", task_profile: Mapping[str, Any] | None = None) -> dict:
    profile = dict(task_profile or {})
    task = str(profile.get("task") or "general_question")
    entities = _comparison_entities(text, language)
    normalized_text = normalize(text)
    if entities and task in {"general_question", "explanation", "factual_definition"}:
        task = "comparison"
    elif task == "general_question":
        if any(cue in normalized_text for cue in ("solve", "equation", "calculate", "compute", "percentage", "λυσε", "εξισωση", "υπολογισε", "ποσοστο")):
            task = "math"
        elif re.search(r"^(?:how (?:do|can|to)|steps? to|guide to|πως να|πώς να)", normalized_text):
            task = "how_to"
        elif re.search(r"^(?:why|how does|how do|γιατι|γιατί|πως λειτουργει|πώς λειτουργεί)", normalized_text):
            task = "causal_explanation"
        elif any(cue in normalized_text for cue in ("recommend", "best for", "which should", "προτεινε", "πρότεινε", "ποιο να")):
            task = "recommendation"
    content_terms = list(profile.get("content_terms") or _tokens(text, language))[:20]
    constraints = _extract_constraints(text, language)
    subquestions = _split_subquestions(text, language)

    if task == "comparison" and not entities:
        likely = [term for term in content_terms if len(term) > 1][:2]
        entities = likely if len(likely) == 2 else []

    expected = {
        "comparison": ["state the central difference", "cover both sides", "give use cases or trade-offs"],
        "how_to": ["give prerequisites", "ordered steps", "verification or failure checks"],
        "coding": ["give usable code or commands", "state assumptions", "mention important failure cases"],
        "math": ["show essential calculation", "state exact final result", "check the result"],
        "causal_explanation": ["state the main cause", "explain the mechanism", "separate cause from correlation"],
        "recommendation": ["identify criteria", "compare trade-offs", "give a conditional recommendation"],
        "summary": ["preserve the main claim", "retain critical numbers or caveats", "remove repetition"],
        "translation": ["preserve meaning", "use natural target-language grammar", "do not add new claims"],
        "factual_definition": ["define directly", "add one useful distinction or example"],
        "explanation": ["answer first", "explain in logical order", "use a concrete example when helpful"],
    }.get(task, ["answer the exact question", "cover all explicit parts", "avoid unsupported claims"])

    complexity = float(profile.get("complexity", 0.5) or 0.5)
    if len(subquestions) > 2:
        complexity = min(1.0, complexity + 0.12)
    if constraints:
        complexity = min(1.0, complexity + 0.08)

    return {
        "task": task,
        "entities": entities,
        "constraints": constraints,
        "subquestions": subquestions,
        "content_terms": content_terms,
        "expected": expected,
        "complexity": round(complexity, 3),
        "thinking_recommended": task in {"math", "coding", "comparison", "causal_explanation", "recommendation"} and complexity >= 0.58,
    }


def _evidence_source_prior(item: Mapping[str, Any]) -> float:
    source_type = str(item.get("source_type") or item.get("kind") or item.get("source") or "local").casefold()
    return _SOURCE_PRIORS.get(source_type, 0.68)


def evidence_diagnostics(query: str, evidence: Sequence[Mapping[str, Any]], language: str = "en", plan: Mapping[str, Any] | None = None) -> dict:
    plan = dict(plan or plan_query(query, language))
    query_terms = set(_tokens(query, language))
    entities = [normalize(value) for value in plan.get("entities", []) if normalize(value)]
    covered_terms: set[str] = set()
    entity_hits: dict[str, int] = {entity: 0 for entity in entities}
    source_types: Counter[str] = Counter()
    numerical_claims: defaultdict[str, list[str]] = defaultdict(list)
    top_score = 0.0

    for item in evidence:
        sentence = str(item.get("sentence") or item.get("text") or item.get("response") or "")
        title = str(item.get("title") or "")
        combined = normalize(title + " " + sentence)
        item_terms = set(_tokens(combined, language))
        covered_terms.update(query_terms & item_terms)
        for entity in entities:
            if entity in combined:
                entity_hits[entity] += 1
        source_type = str(item.get("source_type") or item.get("kind") or item.get("source") or "local")
        source_types[source_type] += 1
        top_score = max(top_score, float(item.get("score", 0.0) or 0.0) * _evidence_source_prior(item))
        for number in _NUMBER_RE.findall(sentence):
            numerical_claims[number.replace(",", ".")].append(title)

    coverage = len(covered_terms) / max(1, len(query_terms))
    entity_coverage = (sum(1 for hits in entity_hits.values() if hits > 0) / len(entity_hits)) if entity_hits else 1.0
    diversity = min(1.0, len(source_types) / 4.0)
    repeated_numbers = {number: titles for number, titles in numerical_claims.items() if len(set(titles)) >= 2}
    confidence = 0.42 * min(1.0, top_score) + 0.30 * coverage + 0.18 * entity_coverage + 0.10 * diversity
    return {
        "coverage": round(coverage, 3),
        "entity_coverage": round(entity_coverage, 3),
        "entity_hits": entity_hits,
        "source_types": dict(source_types),
        "source_diversity": round(diversity, 3),
        "corroborated_numbers": repeated_numbers,
        "confidence": round(max(0.0, min(1.0, confidence)), 3),
    }


def build_reasoning_brief(
    query: str,
    language: str,
    task_profile: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
    deterministic_draft: str = "",
    max_chars: int = 1800,
) -> tuple[str, dict]:
    plan = plan_query(query, language, task_profile)
    diagnostics = evidence_diagnostics(query, evidence, language, plan)
    labels = {
        "task": "TASK" if language != "el" else "ΕΡΓΑΣΙΑ",
        "entities": "ENTITIES" if language != "el" else "ΟΝΤΟΤΗΤΕΣ",
        "must": "MUST COVER" if language != "el" else "ΠΡΕΠΕΙ ΝΑ ΚΑΛΥΨΕΙ",
        "constraints": "CONSTRAINTS" if language != "el" else "ΠΕΡΙΟΡΙΣΜΟΙ",
        "draft": "SAFE GROUNDED DRAFT" if language != "el" else "ΑΣΦΑΛΕΣ ΤΕΚΜΗΡΙΩΜΕΝΟ ΠΡΟΣΧΕΔΙΟ",
        "warning": "GROUNDING RULE" if language != "el" else "ΚΑΝΟΝΑΣ ΤΕΚΜΗΡΙΩΣΗΣ",
    }
    lines = [f"{labels['task']}: {plan['task']}"]
    if plan["entities"]:
        lines.append(f"{labels['entities']}: " + " | ".join(str(value) for value in plan["entities"]))
    lines.append(f"{labels['must']}: " + "; ".join(str(value) for value in plan["expected"]))
    if plan["constraints"]:
        lines.append(f"{labels['constraints']}: " + "; ".join(str(value) for value in plan["constraints"]))
    grounding = (
        "Use only supported facts from the evidence or exact tool result. Do not fill gaps with plausible guesses."
        if language != "el" else
        "Χρησιμοποίησε μόνο γεγονότα που υποστηρίζονται από τα στοιχεία ή από ακριβές αποτέλεσμα εργαλείου. Μην καλύπτεις κενά με πιθανές εικασίες."
    )
    lines.append(f"{labels['warning']}: {grounding}")
    if deterministic_draft:
        draft = re.sub(r"\s+", " ", deterministic_draft).strip()
        lines.append(f"{labels['draft']}: {draft[:900]}")
    brief = "\n".join(lines)
    return brief[:max_chars], {"plan": plan, "diagnostics": diagnostics}


def _dedupe_sentences(values: Iterable[str]) -> list[str]:
    output: list[str] = []
    normalized: list[str] = []
    for value in values:
        sentence = re.sub(r"\s+", " ", str(value)).strip(" -\t")
        key = normalize(sentence)
        if len(sentence) < 12 or not key:
            continue
        if any(key == prior or (len(key) > 30 and (key in prior or prior in key)) for prior in normalized):
            continue
        normalized.append(key)
        output.append(sentence)
    return output


def synthesize_grounded_answer(
    query: str,
    evidence: Sequence[Mapping[str, Any]],
    language: str = "en",
    task_profile: Mapping[str, Any] | None = None,
    max_sentences: int = 6,
) -> dict:
    """Construct a stable evidence-only answer for small-model fallback or draft."""
    if not evidence:
        return {"response": "", "confidence": 0.0, "route": "grounded_empty"}
    plan = plan_query(query, language, task_profile)
    diagnostics = evidence_diagnostics(query, evidence, language, plan)
    task = plan["task"]
    ranked = sorted(
        evidence,
        key=lambda item: float(item.get("score", 0.0) or 0.0) * _evidence_source_prior(item),
        reverse=True,
    )
    sentences = _dedupe_sentences(str(item.get("sentence") or item.get("text") or item.get("response") or "") for item in ranked)
    if not sentences:
        return {"response": "", "confidence": 0.0, "route": "grounded_empty"}

    response = ""
    entities = [str(value) for value in plan.get("entities", [])]
    if task == "comparison" and len(entities) == 2:
        groups: list[list[str]] = [[], []]
        shared: list[str] = []
        for sentence in sentences:
            haystack = normalize(sentence)
            hits = [index for index, entity in enumerate(entities) if normalize(entity) in haystack]
            if len(hits) == 1:
                groups[hits[0]].append(sentence)
            else:
                shared.append(sentence)
        lines = []
        if language != "el":
            lines.append(f"{entities[0]} and {entities[1]} differ mainly in their purpose, behavior, or trade-offs:")
        else:
            lines.append(f"Τα {entities[0]} και {entities[1]} διαφέρουν κυρίως στον σκοπό, στη λειτουργία ή στους συμβιβασμούς τους:")
        for index, entity in enumerate(entities):
            chosen = _dedupe_sentences(groups[index])[:2]
            if chosen:
                lines.append(f"- {entity}: " + " ".join(chosen))
        if shared:
            label = "Practical distinction" if language != "el" else "Πρακτική διάκριση"
            lines.append(f"- {label}: {shared[0]}")
        response = "\n".join(lines)
    elif task in {"how_to", "coding"}:
        heading = "Recommended procedure:" if language != "el" else "Προτεινόμενη διαδικασία:"
        response = heading + "\n" + "\n".join(f"{index}. {sentence}" for index, sentence in enumerate(sentences[:max_sentences], 1))
    elif task == "causal_explanation":
        heading = "Main explanation:" if language != "el" else "Κύρια εξήγηση:"
        first = sentences[0]
        remaining = sentences[1:max_sentences]
        response = heading + " " + first
        if remaining:
            mechanism = "Mechanism:" if language != "el" else "Μηχανισμός:"
            response += "\n" + mechanism + "\n" + "\n".join(f"- {sentence}" for sentence in remaining)
    elif task == "recommendation":
        heading = "Evidence-based guidance:" if language != "el" else "Καθοδήγηση βάσει στοιχείων:"
        response = heading + "\n" + "\n".join(f"- {sentence}" for sentence in sentences[:max_sentences])
    elif task in {"factual_definition", "explanation", "general_question"}:
        response = " ".join(sentences[:max_sentences])
    else:
        response = " ".join(sentences[:max_sentences])

    confidence = float(diagnostics["confidence"])
    if task == "comparison" and diagnostics["entity_coverage"] < 1.0:
        confidence *= 0.70
    if response:
        confidence = max(0.45, confidence)
    return {
        "response": response.strip(),
        "confidence": round(min(0.96, confidence), 3),
        "route": "advanced_grounded_synthesis",
        "plan": plan,
        "diagnostics": diagnostics,
    }


def audit_answer(
    answer: str,
    question: str,
    evidence: Sequence[Mapping[str, Any]] = (),
    language: str = "en",
    task_profile: Mapping[str, Any] | None = None,
) -> dict:
    clean = str(answer).strip()
    if not clean:
        return {"score": 0.0, "issues": ["empty"], "coverage": 0.0}
    plan = plan_query(question, language, task_profile)
    issues: list[str] = []
    score = 0.50
    normalized = normalize(clean)

    leakage_markers = ("<|im_start|>", "<|im_end|>", "USER QUESTION", "EVIDENCE (", "SAFE GROUNDED DRAFT")
    if any(marker.casefold() in clean.casefold() for marker in leakage_markers):
        issues.append("prompt leakage")
        score -= 0.38

    greek = sum(1 for char in clean.casefold() if "α" <= char <= "ω")
    latin = sum(1 for char in clean.casefold() if "a" <= char <= "z")
    if language == "el" and latin > max(35, greek * 2.5):
        issues.append("wrong output language")
        score -= 0.32
    elif language == "en" and greek > max(25, latin):
        issues.append("wrong output language")
        score -= 0.32

    question_terms = set(_tokens(question, language))
    answer_terms = set(_tokens(clean, language))
    overlap = len(question_terms & answer_terms) / max(1, min(12, len(question_terms)))
    score += min(0.20, overlap * 0.28)
    if len(question_terms) >= 3 and overlap < 0.08:
        issues.append("weak relevance")
        score -= 0.18

    entities = [normalize(value) for value in plan.get("entities", []) if normalize(value)]
    missing_entities = [entity for entity in entities if entity not in normalized]
    if missing_entities:
        issues.append("missing comparison side")
        score -= 0.12 * min(2, len(missing_entities))
    elif entities:
        score += 0.10

    task = plan["task"]
    if task in {"how_to", "coding"}:
        if not (re.search(r"(?m)^\s*(?:\d+[.)]|[-*])\s+", clean) or "```" in clean or re.search(r"\b(?:run|install|open|create|τρεξε|εγκαταστησε|άνοιξε)\b", normalized)):
            issues.append("missing actionable steps")
            score -= 0.12
        else:
            score += 0.08
    if task == "causal_explanation":
        if not any(cue in normalized for cue in ("because", "therefore", "due to", "causes", "mechanism", "επειδη", "διοτι", "προκαλει", "μηχανισμος")):
            issues.append("weak causal mechanism")
            score -= 0.10
    if task == "math" and not re.search(r"\d|=", clean):
        issues.append("missing mathematical result")
        score -= 0.18

    lines = [normalize(line) for line in clean.splitlines() if normalize(line)]
    if len(lines) >= 3 and len(set(lines)) / len(lines) < 0.72:
        issues.append("repetitive")
        score -= 0.20
    words = _tokens(clean, language, keep_stop=True)
    if len(words) < 5:
        issues.append("too short")
        score -= 0.18
    elif len(words) >= 18:
        score += 0.06

    # Flag unsupported precise numbers. This is a warning, not an automatic rejection,
    # because dates and common constants may be legitimately inferred.
    support_text = question + " " + " ".join(
        str(item.get("sentence") or item.get("text") or item.get("response") or "") for item in evidence
    )
    supported_numbers = {value.replace(",", ".") for value in _NUMBER_RE.findall(support_text)}
    answer_numbers = {value.replace(",", ".") for value in _NUMBER_RE.findall(clean)}
    unsupported = sorted(value for value in answer_numbers - supported_numbers if value not in {"0", "1", "2", "3", "4", "5", "10", "100"})
    if unsupported:
        issues.append("unverified precise numbers")
        score -= min(0.12, 0.025 * len(unsupported))

    if clean[-1:] not in ".!?`)]}" and len(clean) > 45:
        issues.append("possibly truncated")
        score -= 0.08

    return {
        "score": round(max(0.0, min(1.0, score)), 3),
        "issues": issues,
        "coverage": round(overlap, 3),
        "missing_entities": missing_entities,
        "unsupported_numbers": unsupported,
        "plan": plan,
    }


def choose_or_repair_answer(
    generated: str,
    grounded: str,
    audit: Mapping[str, Any],
    language: str = "en",
) -> tuple[str, dict]:
    """Choose the safer answer and explain the deterministic decision."""
    generated = str(generated).strip()
    grounded = str(grounded).strip()
    score = float(audit.get("score", 0.0) or 0.0)
    severe = {"prompt leakage", "wrong output language", "missing comparison side"} & set(audit.get("issues", []))
    if grounded and (not generated or score < 0.48 or severe):
        return grounded, {"decision": "grounded_replacement", "generated_score": score, "issues": list(audit.get("issues", []))}
    if grounded and score < 0.64:
        # Preserve a useful generated detail only when it is not just a repetition.
        generated_norm, grounded_norm = normalize(generated), normalize(grounded)
        if generated_norm and generated_norm not in grounded_norm and grounded_norm not in generated_norm and len(generated) < 900:
            label = "Additional model explanation:" if language != "el" else "Πρόσθετη εξήγηση μοντέλου:"
            return grounded + "\n\n" + label + " " + generated, {
                "decision": "grounded_plus_generated", "generated_score": score, "issues": list(audit.get("issues", []))
            }
        return grounded, {"decision": "grounded_replacement", "generated_score": score, "issues": list(audit.get("issues", []))}
    return generated, {"decision": "generated_kept", "generated_score": score, "issues": list(audit.get("issues", []))}
