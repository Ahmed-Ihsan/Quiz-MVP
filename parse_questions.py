#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse content.text and extract MCQ questions into questions.json."""
import json
import re
import os

CONTENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content.text")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questions.json")

# Sections to EXCLUDE (practical questions)
EXCLUDE_SECTIONS = [
    "السؤال العملي: اكتشف أخطاء التوصيل",
    "السؤال العملي: صمّم مشروعك بنفسك",
]

# Correct answers keyed by (section_title, question_number) -> option letter
# Determined from technical analysis of each question.
CORRECT_ANSWERS = {
    # Section 1: أسئلة متقدمة قليلًا عن الأردوينو والحساسات (15 Q)
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 1): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 2): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 3): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 4): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 5): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 6): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 7): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 8): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 9): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 10): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 11): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 12): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 13): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 14): "أ",
    ("أسئلة متقدمة قليلًا عن الأردوينو والحساسات", 15): "أ",

    # Section 2: أسئلة عن أكواد بسيطة في الأردوينو وبايثون (20 Q, Arduino 1-10, Python 11-20)
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 1): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 2): "ب",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 3): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 4): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 5): "ب",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 6): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 7): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 8): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 9): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 10): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 11): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 12): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 13): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 14): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 15): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 16): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 17): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 18): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 19): "أ",
    ("أسئلة عن أكواد بسيطة في الأردوينو وبايثون", 20): "أ",

    # Section 3: أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون (15 Q, Arduino 1-7, Python 8-15)
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 1): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 2): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 3): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 4): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 5): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 6): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 7): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 8): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 9): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 10): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 11): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 12): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 13): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 14): "أ",
    ("أسئلة متوسطة الصعوبة عن أكواد الأردوينو وبايثون", 15): "أ",

    # Section 4: أسئلة تحليل أكواد (مستوى أعلى قليلًا) (15 Q, Arduino 1-6, Python 7-15)
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 1): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 2): "ج",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 3): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 4): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 5): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 6): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 7): "ب",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 8): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 9): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 10): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 11): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 12): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 13): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 14): "أ",
    ("أسئلة تحليل أكواد (مستوى أعلى قليلًا)", 15): "أ",

    # Section 7: أسئلة بسيطة عن إنترنت الأشياء (IoT) (10 Q)
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 1): "أ",
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 2): "أ",
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 3): "أ",
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 4): "أ",
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 5): "أ",
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 6): "أ",
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 7): "أ",
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 8): "أ",
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 9): "أ",
    ("أسئلة بسيطة عن إنترنت الأشياء (IoT)", 10): "أ",

    # Section 8: أسئلة عن الكلمات المحجوزة في Arduino و Python (20 Q, Arduino 1-10, Python 11-20)
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 1): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 2): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 3): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 4): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 5): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 6): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 7): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 8): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 9): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 10): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 11): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 12): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 13): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 14): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 15): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 16): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 17): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 18): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 19): "أ",
    ("أسئلة عن الكلمات المحجوزة في Arduino و Python", 20): "أ",
}


def parse_content(text):
    """Parse the content.text and extract MCQ questions."""
    lines = text.split("\n")
    questions = []
    current_section = None
    current_subsection = None
    i = 0
    qid = 0

    while i < len(lines):
        line = lines[i]

        # Detect section header (# ...)
        if line.startswith("# ") and not line.startswith("## "):
            current_section = line[2:].strip()
            current_subsection = None
            i += 1
            continue

        # Detect subsection (## ...)
        if line.startswith("## ") and not line.startswith("### "):
            current_subsection = line[3:].strip()
            i += 1
            continue

        # Skip excluded sections
        if current_section and any(current_section.startswith(ex) for ex in EXCLUDE_SECTIONS):
            i += 1
            continue

        # Detect question header (### N. ...)
        qmatch = re.match(r"^###\s+(\d+)\.\s+(.*)", line)
        if qmatch and current_section and not any(current_section.startswith(ex) for ex in EXCLUDE_SECTIONS):
            qnum = int(qmatch.group(1))
            qtext = qmatch.group(2).strip()
            i += 1

            # Check for code block after question text
            code = None
            # Skip blank lines
            while i < len(lines) and lines[i].strip() == "":
                i += 1

            # Check for code block
            if i < len(lines) and lines[i].strip().startswith("```"):
                code_lines = []
                # Skip the opening ``` line
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                # Skip closing ```
                if i < len(lines):
                    i += 1
                code = "\n".join(code_lines)

            # Now parse options
            options = {}
            # Some questions have code blocks as options (multi-line answers)
            # We need to handle the special case where options are code blocks
            # Skip blank lines before options
            while i < len(lines) and lines[i].strip() == "":
                i += 1

            # Parse options - handle both simple and complex (code-block) options
            option_order = []
            option_texts = {}
            while i < len(lines):
                oline = lines[i]
                # Option line: - أ) text  or  - أ) (then code block follows)
                omatch = re.match(r"^-\s*([أبجد])\)\s*(.*)", oline)
                if omatch:
                    letter = omatch.group(1)
                    rest = omatch.group(2).strip()
                    # Check if the option text is empty (code block follows)
                    if rest == "" and i + 1 < len(lines) and lines[i + 1].strip().startswith("```"):
                        # Multi-line code option
                        i += 1  # skip current option line
                        i += 1  # skip opening ```
                        code_opt_lines = []
                        while i < len(lines) and not lines[i].strip().startswith("```"):
                            code_opt_lines.append(lines[i])
                            i += 1
                        if i < len(lines):
                            i += 1  # skip closing ```
                        rest = "\n".join(code_opt_lines)
                    option_order.append(letter)
                    option_texts[letter] = rest
                    i += 1
                elif oline.strip() == "" or oline.strip() == "---":
                    # End of options (blank line or separator)
                    if option_order:  # we have options already, so this is end
                        i += 1
                        break
                    i += 1
                elif oline.startswith("### ") or oline.startswith("# ") or oline.startswith("## "):
                    # Next question/section
                    break
                else:
                    # Unexpected line, stop
                    break

            # Build the question
            if len(option_order) >= 2:
                qid += 1
                # Determine section label (include subsection if present)
                section_label = current_section
                if current_subsection:
                    section_label = current_section + " - " + current_subsection

                # Get correct answer
                correct = CORRECT_ANSWERS.get((current_section, qnum), "أ")

                q = {
                    "id": qid,
                    "section": section_label,
                    "question": qtext,
                    "code": code,
                    "options": {l: option_texts[l] for l in option_order},
                    "correct_answer": correct,
                }
                questions.append(q)
            continue

        i += 1

    return questions


def main():
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    questions = parse_content(text)

    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(questions)} questions")
    # Print summary by section
    from collections import Counter
    sections = Counter(q["section"] for q in questions)
    for s, c in sections.items():
        print(f"  {s}: {c}")

    # Verify all have correct_answer
    missing = [q["id"] for q in questions if not q.get("correct_answer")]
    if missing:
        print(f"WARNING: {len(missing)} questions missing correct_answer: {missing}")
    else:
        print("All questions have correct_answer.")


if __name__ == "__main__":
    main()
