"""Level 2, Build: document extraction pipeline with validation.

Pipeline per document:

1. Pick the deterministic extractor for the document type. The
   extractors are regex and rule based. No language model is
   involved, and this file does not claim one is.
2. The extractor returns a candidate record. Typed fields are
   converted only when the token parses cleanly (a total of 249.50
   becomes the number 249.5). A token that does not parse stays a
   string, so the validator sees the type error instead of the
   extractor hiding it by coercion or by dropping the field.
3. The candidate is validated against the strict schema for its
   type with the Level 1 Learn validator, reused unchanged.
4. Routing: a candidate with no validation errors goes to the
   accepted list. A candidate with any error goes to the rejected
   list with the full validator error list. Nothing is silently
   passed, repaired, or dropped at this level.

Unknown document types are rejected with a structured error at
path $, code unknown_type, without calling any extractor.
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_LEARN = os.path.join(os.path.dirname(_HERE), "level-1-learn")
sys.path.insert(0, _LEARN)
from schema_validate import validate  # noqa: E402


# ---------------------------------------------------------------------------
# Strict schemas, one per type. Field order here is the order the
# validator reports property errors in.
# ---------------------------------------------------------------------------

INVOICE_SCHEMA = {
    "type": "object",
    "properties": {
        "invoice_id": {"type": "string", "pattern": "^INV-[0-9]{4}$"},
        "vendor": {"type": "string", "minLength": 1, "maxLength": 80},
        "date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "total_cad": {"type": "number", "minimum": 0.01, "maximum": 100000},
        "items_count": {"type": "integer", "minimum": 1, "maximum": 100},
    },
    "required": ["invoice_id", "vendor", "date", "total_cad", "items_count"],
    "additionalProperties": False,
}

MEETING_SCHEMA = {
    "type": "object",
    "properties": {
        "meeting_id": {"type": "string", "pattern": "^MTG-[0-9]{4}$"},
        "title": {"type": "string", "minLength": 1, "maxLength": 120},
        "date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "attendees": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "minItems": 1,
            "maxItems": 20,
        },
        "duration_minutes": {"type": "integer", "minimum": 15, "maximum": 480},
    },
    "required": ["meeting_id", "title", "date", "attendees", "duration_minutes"],
    "additionalProperties": False,
}

PRODUCT_SCHEMA = {
    "type": "object",
    "properties": {
        "sku": {"type": "string", "pattern": "^SKU-[0-9]{4}$"},
        "name": {"type": "string", "minLength": 1, "maxLength": 80},
        "price_cad": {"type": "number", "minimum": 0.01, "maximum": 50000},
        "stock": {"type": "integer", "minimum": 0, "maximum": 10000},
        "category": {
            "type": "string",
            "enum": ["tools", "kitchen", "office", "outdoor"],
        },
    },
    "required": ["sku", "name", "price_cad", "stock", "category"],
    "additionalProperties": False,
}

SCHEMAS = {
    "invoice": INVOICE_SCHEMA,
    "meeting_note": MEETING_SCHEMA,
    "product_listing": PRODUCT_SCHEMA,
}


# ---------------------------------------------------------------------------
# Conversion helpers. A token that does not parse is returned as the
# raw string, on purpose: the validator then reports a type error
# at that field instead of the error being hidden.
# ---------------------------------------------------------------------------


def _as_number(token):
    try:
        return float(token)
    except (TypeError, ValueError):
        return token


def _as_integer(token):
    try:
        return int(token)
    except (TypeError, ValueError):
        return token


def _line(text, label):
    match = re.search(rf"^{label}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


# ---------------------------------------------------------------------------
# Deterministic extractors, one per type.
# ---------------------------------------------------------------------------


def extract_invoice(text):
    record = {}
    match = re.search(r"^Invoice\s+(\S+)$", text, flags=re.MULTILINE)
    if match:
        record["invoice_id"] = match.group(1)
    vendor = _line(text, "Vendor")
    if vendor is not None:
        record["vendor"] = vendor
    date = _line(text, "Date")
    if date is not None:
        record["date"] = date
    total = _line(text, "Total")
    if total is not None:
        record["total_cad"] = _as_number(total)
    items = _line(text, "Items")
    if items is not None:
        record["items_count"] = _as_integer(items)
    discount = _line(text, "Discount")
    if discount is not None:
        record["discount"] = _as_number(discount)
    return record


def extract_meeting(text):
    record = {}
    match = re.search(r"^Meeting\s+(\S+)$", text, flags=re.MULTILINE)
    if match:
        record["meeting_id"] = match.group(1)
    title = _line(text, "Title")
    if title is not None:
        record["title"] = title
    date = _line(text, "Date")
    if date is not None:
        record["date"] = date
    attendees = _line(text, "Attendees")
    if attendees is not None:
        record["attendees"] = [name.strip() for name in attendees.split(",")]
    duration = _line(text, "Duration")
    if duration is not None:
        record["duration_minutes"] = _as_integer(duration)
    return record


def extract_product(text):
    record = {}
    match = re.search(r"^Product\s+(\S+)$", text, flags=re.MULTILINE)
    if match:
        record["sku"] = match.group(1)
    name = _line(text, "Name")
    if name is not None:
        record["name"] = name
    price = _line(text, "Price")
    if price is not None:
        record["price_cad"] = _as_number(price)
    stock = _line(text, "Stock")
    if stock is not None:
        record["stock"] = _as_integer(stock)
    category = _line(text, "Category")
    if category is not None:
        record["category"] = category
    warranty = _line(text, "Warranty")
    if warranty is not None:
        record["warranty_years"] = _as_integer(warranty)
    return record


EXTRACTORS = {
    "invoice": extract_invoice,
    "meeting_note": extract_meeting,
    "product_listing": extract_product,
}


# ---------------------------------------------------------------------------
# Pipeline.
# ---------------------------------------------------------------------------


def extract_and_validate(document):
    """Extract one document and validate the candidate record.

    Returns a dict with id, doc_type, record, errors, and accepted
    (True when the error list is empty).
    """
    doc_type = document["doc_type"]
    extractor = EXTRACTORS.get(doc_type)
    if extractor is None:
        return {
            "id": document["id"],
            "doc_type": doc_type,
            "record": None,
            "errors": [
                {
                    "path": "$",
                    "code": "unknown_type",
                    "message": f"$: unknown document type {doc_type!r}",
                }
            ],
            "accepted": False,
        }
    record = extractor(document["text"])
    errors = validate(record, SCHEMAS[doc_type])
    return {
        "id": document["id"],
        "doc_type": doc_type,
        "record": record,
        "errors": errors,
        "accepted": not errors,
    }


def run_pipeline(documents):
    """Run every document. Returns (accepted, rejected) lists."""
    accepted = []
    rejected = []
    for document in documents:
        outcome = extract_and_validate(document)
        if outcome["accepted"]:
            accepted.append(outcome)
        else:
            rejected.append(outcome)
    return accepted, rejected
