"""A realistic invoice corpus with ground truth — varied real-world layouts.

Unlike the templated `dataset.make_invoices`, every item here uses a different
format: label variants ("Invoice #", "Document No.", "Ref"), currency as symbol
or code ($/€/£), thousands separators, several date formats, multi-line items,
discounts/VAT, and OCR-style noise. The correct answer is still unambiguous to a
human — but extraction is genuinely non-trivial, so accuracy measured on this set
is real, not a formality.

This stands in for the *text* a UiPath Document Understanding step would emit for
a scanned invoice; swap DU's output in for production. Schema matches
`patient.REQUIRED_FIELDS`: invoice_number, vendor, total, currency, due_date.
"""

from __future__ import annotations

_INVOICES = [
    {
        "id": "real-01-us-standard",
        "text": (
            "ACME INDUSTRIES INC.\n123 Industrial Pkwy, Detroit MI\n\n"
            "INVOICE #  AC-2026-4471\nBill To: Northwind Traders\n"
            "Date issued: 02/14/2026     Payment due: 03/16/2026\n\n"
            "Widgets (x500) .......... $4,250.00\nFreight ................. $   125.50\n"
            "                         -----------\nTotal Due:  $4,375.50\nTerms: Net 30"
        ),
        "ground_truth": {"invoice_number": "AC-2026-4471", "vendor": "ACME INDUSTRIES INC.",
                          "total": 4375.50, "currency": "USD", "due_date": "2026-03-16"},
    },
    {
        "id": "real-02-eu-vat",
        "text": (
            "Globex GmbH\nRechnung / Invoice\nInvoice No.: 2026/DE/0098\n"
            "Kunde: Soylent Foods Ltd\nRechnungsdatum: 05.03.2026\n"
            "Fällig am / Due: 04.04.2026\n\nPosition 1  Sensoren     1.800,00\n"
            "Zwischensumme            1.800,00\nUSt 19%                    342,00\n"
            "Gesamtbetrag  EUR 2.142,00"
        ),
        "ground_truth": {"invoice_number": "2026/DE/0098", "vendor": "Globex GmbH",
                          "total": 2142.00, "currency": "EUR", "due_date": "2026-04-04"},
    },
    {
        "id": "real-03-uk-tax-invoice",
        "text": (
            "TAX INVOICE\nWayne Logistics Ltd.\nVAT Reg 882 4471 09\n\n"
            "Ref: WL-77120\nInvoice date: 11 March 2026\nDue: 25 March 2026\n\n"
            "Courier services for Feb 2026\nSubtotal     £   960.00\nVAT @ 20%    £   192.00\n"
            "Balance Due  £ 1,152.00"
        ),
        "ground_truth": {"invoice_number": "WL-77120", "vendor": "Wayne Logistics Ltd.",
                          "total": 1152.00, "currency": "GBP", "due_date": "2026-03-25"},
    },
    {
        "id": "real-04-noisy-ocr",
        "text": (
            "lNVOlCE\nStark Supplies\n\nlnvoice Number :  SS 30188\n"
            "lssued: 2026-01-09   Due Date: 2026-02-08\n\n"
            "Tota1 Amount Due . . . USD  890.00\nThank you for your  buslness"
        ),
        "ground_truth": {"invoice_number": "SS 30188", "vendor": "Stark Supplies",
                          "total": 890.00, "currency": "USD", "due_date": "2026-02-08"},
    },
    {
        "id": "real-05-remit-bottom",
        "text": (
            "Document No: HC-558843\nDate: 2026/04/02\nNet due within 15 days — pay by 2026/04/17\n\n"
            "Cloud compute (Q1)        12,400.00\nSupport tier Gold          2,600.00\n"
            "Amount Payable: $15,000.00\n\nRemit to: Hooli Cloud Services"
        ),
        "ground_truth": {"invoice_number": "HC-558843", "vendor": "Hooli Cloud Services",
                          "total": 15000.00, "currency": "USD", "due_date": "2026-04-17"},
    },
    {
        "id": "real-06-discount",
        "text": (
            "Initech LLC  —  Invoice\nInvoice: INT-0421-B\nFor: Umbrella Corp\n"
            "Invoice Date: March 1, 2026\nDue Date: March 31, 2026\n\n"
            "Consulting (40h)     $6,000.00\nLoyalty discount      -$600.00\n"
            "Grand Total          $5,400.00 USD"
        ),
        "ground_truth": {"invoice_number": "INT-0421-B", "vendor": "Initech LLC",
                          "total": 5400.00, "currency": "USD", "due_date": "2026-03-31"},
    },
    {
        "id": "real-07-euro-symbol",
        "text": (
            "Soylent Foods\nFACTURE  N°  SF-2026-219\nÉmise: 18/02/2026\n"
            "Échéance: 20/03/2026\n\nMatières premières      €  3 250,00\n"
            "Total TTC               € 3 250,00"
        ),
        "ground_truth": {"invoice_number": "SF-2026-219", "vendor": "Soylent Foods",
                          "total": 3250.00, "currency": "EUR", "due_date": "2026-03-20"},
    },
    {
        "id": "real-08-minimal",
        "text": (
            "Umbrella Corp\nInv 90021\n2026-05-12 (due 2026-06-11)\nBalance: GBP 740.25"
        ),
        "ground_truth": {"invoice_number": "90021", "vendor": "Umbrella Corp",
                          "total": 740.25, "currency": "GBP", "due_date": "2026-06-11"},
    },
    {
        "id": "real-09-po-header",
        "text": (
            "============================\n  WAYNE LOGISTICS\n============================\n"
            "Invoice No ......... WL-77998\nPO Number .......... PO-44213\n"
            "Invoice Date ....... 04/05/2026\nDue Date ........... 05/05/2026\n\n"
            "Pallet shipping x30      $2,970.00\nTOTAL              $2,970.00"
        ),
        "ground_truth": {"invoice_number": "WL-77998", "vendor": "WAYNE LOGISTICS",
                          "total": 2970.00, "currency": "USD", "due_date": "2026-05-05"},
    },
    {
        "id": "real-10-multiline-tax",
        "text": (
            "Stark Supplies — Statement of Charges\nInvoice #: SS-2026-6610\n"
            "Issued 2026-03-22, payable by 2026-04-21\n\n"
            "Item A   2 x 150.00 = 300.00\nItem B   5 x  80.00 = 400.00\n"
            "Item C   1 x 220.00 = 220.00\nSubtotal           920.00\n"
            "Sales tax 8.5%      78.20\nTotal Due  $998.20"
        ),
        "ground_truth": {"invoice_number": "SS-2026-6610", "vendor": "Stark Supplies",
                          "total": 998.20, "currency": "USD", "due_date": "2026-04-21"},
    },
    {
        "id": "real-11-comma-decimal-eu",
        "text": (
            "Globex GmbH\nRe.-Nr. GX-2026-1175\nDatum 28.02.2026\n"
            "Zahlbar bis 14.03.2026\n\nLizenzgebühr             7.999,99 EUR\n"
            "Endbetrag                7.999,99 EUR"
        ),
        "ground_truth": {"invoice_number": "GX-2026-1175", "vendor": "Globex GmbH",
                          "total": 7999.99, "currency": "EUR", "due_date": "2026-03-14"},
    },
    {
        "id": "real-12-dollar-no-code",
        "text": (
            "ACME INDUSTRIES INC.\nInvoice # AC-2026-4990\nDate: 6/1/2026   Due: 7/1/2026\n"
            "Bill To: Initech LLC\n\nMaintenance retainer ........ $1,250.00\n"
            "Amount due: $1,250.00"
        ),
        "ground_truth": {"invoice_number": "AC-2026-4990", "vendor": "ACME INDUSTRIES INC.",
                          "total": 1250.00, "currency": "USD", "due_date": "2026-07-01"},
    },
]


def make_realistic_invoices(n: int | None = None) -> list[dict]:
    """Return the realistic invoice corpus (all of it, or the first `n`)."""
    return _INVOICES if n is None else _INVOICES[:n]
