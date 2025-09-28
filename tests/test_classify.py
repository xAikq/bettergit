from bettergit.core.classify import detect_type_scope


def test_docs_type():
    diff = "--- a/README.md\n+++ b/README.md\n+Added documentation line\n"
    files = ["README.md"]
    ctype, scope = detect_type_scope(diff, files, cfg=None)
    assert ctype == "docs"
