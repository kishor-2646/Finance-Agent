"""Rule-based categorizer.

Rules decide the category when a known merchant/keyword matches; otherwise the
model's category is kept (if valid), otherwise "Other". Deterministic, free,
and easy to extend: just add keywords to RULES.
"""
import re

CATEGORIES = [
    "Food", "Groceries", "Transport", "Shopping", "Bills", "Entertainment",
    "Health", "Personal Care", "Education", "Transfer", "Other",
]

# category -> keywords (lowercase). Matched as whole words/phrases.
RULES = {
    "Food": [
        "swiggy", "zomato", "dominos", "domino's", "kfc", "mcdonalds", "mcdonald's",
        "burger king", "subway", "pizza hut", "starbucks", "cafe coffee day", "ccd",
        "barbeque nation", "restaurant", "cafe", "biryani", "bakery", "juice",
        "tea stall", "chai", "hotel", "mess", "canteen", "food",
    ],
    "Groceries": [
        "bigbasket", "blinkit", "zepto", "instamart", "dmart", "avenue supermarts",
        "reliance fresh", "more supermarket", "kirana", "supermarket", "super market",
        "provision", "grocery", "groceries", "vegetable", "vegetables", "milk",
        "nilgiris", "spencer", "fruits", "general store",
    ],
    "Transport": [
        "uber", "ola", "rapido", "redbus", "irctc", "metro", "fastag", "indigo",
        "air india", "spicejet", "makemytrip", "goibibo", "petrol", "fuel",
        "indian oil", "bharat petroleum", "hp petrol", "shell", "namma yatri",
        "bus", "railway", "cab", "auto",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "meesho", "croma", "reliance digital",
        "decathlon", "lifestyle", "max fashion", "pantaloons", "westside", "retail",
        "mall", "mart", "store", "shop", "fashion", "electronics",
    ],
    "Bills": [
        "tneb", "tangedco", "bescom", "electricity", "eb bill", "airtel", "jio",
        "vodafone", "bsnl", "recharge", "broadband", "act fibernet", "gas", "indane",
        "water bill", "dth", "tata play", "insurance", "lic", "bill", "postpaid",
        "prepaid", "rent",
    ],
    "Entertainment": [
        "netflix", "spotify", "hotstar", "prime video", "bookmyshow", "pvr", "inox",
        "youtube", "sony liv", "sonyliv", "zee5", "movie", "cinema", "theatre",
        "gaming", "steam", "playstation",
    ],
    "Health": [
        "apollo", "pharmacy", "medplus", "1mg", "pharmeasy", "netmeds", "hospital",
        "clinic", "diagnostic", "diagnostics", "lab", "doctor", "dental", "medical",
        "medicals", "gym", "fitness", "cult fit", "cultfit",
    ],
    "Personal Care": [
        "spa", "salon", "saloon", "parlour", "parlor", "barber", "nykaa",
        "urban company", "beauty", "grooming",
    ],
    "Education": [
        "college", "school", "university", "institute", "tuition", "coursera",
        "udemy", "byju", "byjus", "unacademy", "fees", "academy", "exam", "nit",
        "iit", "library",
    ],
}

# Pre-compile one regex per keyword. Whole-word matching stops "ola" matching
# "Kolathur" or "gas" matching "Vegas".
_PATTERNS = []
for _cat, _words in RULES.items():
    for _w in _words:
        _norm = re.sub(r"[^a-z0-9]+", " ", _w.lower()).strip()
        _PATTERNS.append((_cat, _norm, re.compile(rf"(?<![a-z0-9]){re.escape(_norm)}(?![a-z0-9])")))


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def rule_category(merchant):
    """Return the category from rules, or None. Longest matching keyword wins,
    so 'swiggy instamart' -> Groceries (via 'instamart'), not Food."""
    if not merchant:
        return None
    text = _normalize(str(merchant))
    best = None  # (keyword_length, category)
    for cat, kw, pat in _PATTERNS:
        if pat.search(text) and (best is None or len(kw) > best[0]):
            best = (len(kw), cat)
    return best[1] if best else None


def categorize(merchant, model_category=None):
    """Return (category, source). source is 'rule', 'model' or 'default'."""
    cat = rule_category(merchant)
    if cat:
        return cat, "rule"
    if model_category in CATEGORIES:
        return model_category, "model"
    return "Other", "default"
