"""Level 2, Build: synthetic document corpus. Stdlib only.

All 16 documents in this file are synthetic. They were authored for
this level to exercise the extraction pipeline. No real invoice,
meeting, or product is represented.

Format: each document is a dict with id, doc_type, and text. The
text is plain line-based text. Valid documents carry every field
their type requires, in the form the extractor expects. Malformed
documents carry exactly one designed defect each, named in the
evaluation set (evaluation.json), so a rejection can be checked
against the field it was designed to fail on.

Types: invoice (5 documents valid or malformed in the invoice
shape), meeting_note, product_listing. Counts by expected outcome
are in evaluation.json, not assumed here.
"""

DOCUMENTS = [
    {
        "id": "d01-invoice-valid",
        "doc_type": "invoice",
        "text": (
            "Invoice INV-1001\n"
            "Vendor: Northlight Supplies\n"
            "Date: 2026-10-02\n"
            "Total: 249.50\n"
            "Items: 4\n"
        ),
    },
    {
        "id": "d02-invoice-valid",
        "doc_type": "invoice",
        "text": (
            "Invoice INV-1002\n"
            "Vendor: Paper Trail Office Co\n"
            "Date: 2026-10-05\n"
            "Total: 89.99\n"
            "Items: 2\n"
        ),
    },
    {
        "id": "d03-meeting-valid",
        "doc_type": "meeting_note",
        "text": (
            "Meeting MTG-2001\n"
            "Title: Sprint Planning\n"
            "Date: 2026-10-03\n"
            "Attendees: Ana, Ben, Cara\n"
            "Duration: 60\n"
        ),
    },
    {
        "id": "d04-meeting-valid",
        "doc_type": "meeting_note",
        "text": (
            "Meeting MTG-2002\n"
            "Title: Vendor Review\n"
            "Date: 2026-10-06\n"
            "Attendees: Dev, Eli\n"
            "Duration: 45\n"
        ),
    },
    {
        "id": "d05-product-valid",
        "doc_type": "product_listing",
        "text": (
            "Product SKU-3001\n"
            "Name: Steel Hammer\n"
            "Price: 24.99\n"
            "Stock: 140\n"
            "Category: tools\n"
        ),
    },
    {
        "id": "d06-product-valid",
        "doc_type": "product_listing",
        "text": (
            "Product SKU-3002\n"
            "Name: Ceramic Mug Set\n"
            "Price: 39.50\n"
            "Stock: 65\n"
            "Category: kitchen\n"
        ),
    },
    {
        "id": "d07-invoice-valid",
        "doc_type": "invoice",
        "text": (
            "Invoice INV-1003\n"
            "Vendor: Harbour Print Works\n"
            "Date: 2026-10-09\n"
            "Total: 1200.00\n"
            "Items: 12\n"
        ),
    },
    {
        "id": "d08-meeting-valid",
        "doc_type": "meeting_note",
        "text": (
            "Meeting MTG-2003\n"
            "Title: Hiring Debrief\n"
            "Date: 2026-10-10\n"
            "Attendees: Ana, Farah, Dev, Eli\n"
            "Duration: 90\n"
        ),
    },
    {
        "id": "d09-invoice-missing-vendor",
        "doc_type": "invoice",
        "text": (
            "Invoice INV-1004\n"
            "Date: 2026-10-11\n"
            "Total: 150.00\n"
            "Items: 3\n"
        ),
    },
    {
        "id": "d10-invoice-bad-total-type",
        "doc_type": "invoice",
        "text": (
            "Invoice INV-1005\n"
            "Vendor: Northlight Supplies\n"
            "Date: 2026-10-12\n"
            "Total: FREE\n"
            "Items: 1\n"
        ),
    },
    {
        "id": "d11-invoice-extra-field",
        "doc_type": "invoice",
        "text": (
            "Invoice INV-1006\n"
            "Vendor: Paper Trail Office Co\n"
            "Date: 2026-10-13\n"
            "Total: 75.25\n"
            "Items: 2\n"
            "Discount: 5\n"
        ),
    },
    {
        "id": "d12-invoice-total-out-of-range",
        "doc_type": "invoice",
        "text": (
            "Invoice INV-1007\n"
            "Vendor: Harbour Print Works\n"
            "Date: 2026-10-14\n"
            "Total: 250000.00\n"
            "Items: 5\n"
        ),
    },
    {
        "id": "d13-meeting-missing-title",
        "doc_type": "meeting_note",
        "text": (
            "Meeting MTG-2004\n"
            "Date: 2026-10-15\n"
            "Attendees: Ana, Ben\n"
            "Duration: 30\n"
        ),
    },
    {
        "id": "d14-meeting-duration-out-of-range",
        "doc_type": "meeting_note",
        "text": (
            "Meeting MTG-2005\n"
            "Title: All Hands\n"
            "Date: 2026-10-16\n"
            "Attendees: Ana, Ben, Cara\n"
            "Duration: 900\n"
        ),
    },
    {
        "id": "d15-product-bad-stock-type",
        "doc_type": "product_listing",
        "text": (
            "Product SKU-3003\n"
            "Name: Desk Lamp\n"
            "Price: 54.00\n"
            "Stock: many\n"
            "Category: office\n"
        ),
    },
    {
        "id": "d16-product-bad-category",
        "doc_type": "product_listing",
        "text": (
            "Product SKU-3004\n"
            "Name: Plush Toy\n"
            "Price: 19.99\n"
            "Stock: 200\n"
            "Category: toys\n"
        ),
    },
]
