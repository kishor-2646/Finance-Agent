from categorizer import categorize, rule_category

# (merchant, model_category, expected_category, expected_source)
CASES = [
    # merchants from your own test set
    ("Swiggy", "Food", "Food", "rule"),
    ("Zomato", "Shopping", "Food", "rule"),              # rule overrides a wrong model guess
    ("Kirana Store", "Shopping", "Groceries", "rule"),
    ("Amirtha Super Market", "Shopping", "Groceries", "rule"),
    ("TNEB", "Other", "Bills", "rule"),
    ("TNEB Bill", "Other", "Bills", "rule"),
    ("AJIO", "Shopping", "Shopping", "rule"),
    ("Serenity Spa", "Health", "Personal Care", "rule"),
    ("Serenity Retail", "Other", "Shopping", "rule"),
    ("National Institute of Technology, Trichy", "Transfer", "Education", "rule"),
    # longest keyword wins
    ("Swiggy Instamart", "Food", "Groceries", "rule"),
    # whole-word matching: 'ola' must not match inside other words
    ("Kolathur", None, "Other", "default"),              # 'ola' inside a word must not match
    # no rule: keep the model's category
    ("Arun", "Transfer", "Transfer", "model"),
    ("Rahul (Friend)", "Transfer", "Transfer", "model"),
    # nothing at all
    (None, "Other", "Other", "model"),
    (None, None, "Other", "default"),
    ("Some Unknown Merchant", "Nonsense", "Other", "default"),
]


def test_cases():
    for merchant, model_cat, want_cat, want_src in CASES:
        got = categorize(merchant, model_cat)
        assert got == (want_cat, want_src), f"{merchant!r}: expected {(want_cat, want_src)}, got {got}"


def test_whole_word_matching():
    assert rule_category("Kolathur") is None            # 'ola' inside a word must not match
    assert rule_category("Vegas Club") is None          # 'gas' inside a word must not match
    assert rule_category("Ola Cabs") == "Transport"


if __name__ == "__main__":
    test_cases()
    test_whole_word_matching()
    print("All categorizer tests passed")
