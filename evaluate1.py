"""
Phase 1 Evaluation — Manual test set with ground truth keyword matching.
Usage: python evaluate.py
"""

from rag import build_chain

# Each test case: (question, keyword_that_must_appear_in_answer)
# Keywords are kept simple — a single fact that must be present
TEST_CASES = [
    # --- Fact Sheet ---
    ("What is the ERASMUS code for TH Bingen?",                             "BINGEN01"),
    ("What is the application deadline for winter term exchange students?",  "2024"),
    ("What is the application deadline for summer term exchange students?",  "2024"),
    ("What is the tuition fee per semester for incoming exchange students?", "213"),
    ("What is the minimum language level required for German programs?",     "German"),
    ("What is the minimum language level required for English programs?",    "English"),
    ("What is the application portal for incoming exchange students?",       "inCampo"),
    ("Who is the incoming coordinator at TH Bingen?",                       "Scarongella"),
    ("What is the email address of the International Office?",              "th-bingen.de"),

    # --- Dormitories ---
    ("What is the rent for an Inter 2 apartment?",                          "367"),
    ("What is the rent for a wheelchair accessible apartment in Inter 2?",  "564"),
    ("What is the rent for a family apartment in Inter 2?",                 "Inter 2"),
    ("How far is Inter 2 from the HS campus?",                             "10"),
    ("What is the rent for a Weisenau apartment?",                          "330"),
    ("What is the rent for a pair apartment in Weisenau?",                  "594"),
    ("What is the rent for a Binger Schlag apartment?",                     "357"),
    ("How far is Binger Schlag from the university campus?",                "2"),

    # --- Enrollment / Regulations ---
    ("What language certificate is required for international students?",    "language"),
    ("How long can a student take leave of absence for childcare?",         "six"),
    ("How long can students use IT services after deregistration?",         "three"),

    # --- Visa ---
    ("What documents are needed for a German student visa?",                "passport"),

    # --- Programs ---
    ("What is the workload for the Artificial Intelligence module in MSc Computer Science?", "180"),
    ("How many ECTS is the Artificial Intelligence module worth?",          "6"),
    ("In which language is the Mathematics 1 module taught?",               "German"),
]


def run_evaluation(chain):
    print("=" * 60)
    print("StudyBridge RAG Evaluation")
    print("=" * 60)

    passed = 0
    failed = []

    for i, (question, keyword) in enumerate(TEST_CASES, 1):
        try:
            answer = chain.invoke(question)
            ok = keyword.lower() in answer.lower()
        except Exception as e:
            answer = f"ERROR: {e}"
            ok = False

        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"\n[{i:02d}] {status}")
        print(f"  Q: {question}")
        if not ok:
            print(f"  Expected keyword: '{keyword}'")
            print(f"  Answer: {answer[:200]}")
            failed.append((question, keyword, answer))
        passed += ok

    total = len(TEST_CASES)
    score = 100 * passed // total

    print("\n" + "=" * 60)
    print(f"RESULT: {passed}/{total} passed ({score}%)")
    print("=" * 60)

    if failed:
        print(f"\n{len(failed)} failed questions:")
        for q, kw, ans in failed:
            print(f"  - {q[:60]} (expected: '{kw}')")

    return score


if __name__ == "__main__":
    print("Loading RAG chain...")
    chain = build_chain()
    run_evaluation(chain)
