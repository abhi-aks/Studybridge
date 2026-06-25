"""
Evaluate2 — 10 fresh test cases, different from evaluate1.
Usage: python evaluate2.py
"""

from rag import build_chain

TEST_CASES = [
    # Dormitories
    ("What year was the Münchfeld dormitory built?",                        "2010"),
    ("How many bed places does the Kisselberg dormitory have?",             "792"),

    # Fact Sheet
    ("What is the PIC number of TH Bingen?",                               "949602647"),
    ("What is the phone number of the incoming coordinator?",               "409"),

    # Visa
    ("What is the purpose of the blocked account for student visa?",       "financial"),

    # Module handbooks
    ("What is the exam format for the Artificial Intelligence module?",    "oral"),
    ("How many contact hours does the Artificial Intelligence module have?",""),

    # Programs
    ("What is the duration of the MSc Computer Science program?",          "3"),

    # General TH Bingen
    ("Where is TH Bingen located?",                                        "Bingen"),

    # Enrollment
    ("What happens if a student misses the enrollment deadline?",          "enroll"),
]


def run_evaluation(chain):
    print("=" * 60)
    print("StudyBridge RAG Evaluation — evaluate2")
    print("=" * 60)

    passed = 0
    failed = []

    for i, (question, keyword) in enumerate(TEST_CASES, 1):
        try:
            answer = chain.invoke(question)
            ok = keyword.lower() in answer.lower() if keyword else len(answer) > 50
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
    print("\n" + "=" * 60)
    print(f"RESULT: {passed}/{total} passed ({100 * passed // total}%)")
    print("=" * 60)

    if failed:
        print(f"\n{len(failed)} failed questions:")
        for q, kw, _ in failed:
            print(f"  - {q[:60]} (expected: '{kw}')")


if __name__ == "__main__":
    print("Loading RAG chain...")
    chain = build_chain()
    run_evaluation(chain)
