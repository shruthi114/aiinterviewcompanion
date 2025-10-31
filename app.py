import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # ✅ Safe method


from dotenv import load_dotenv
load_dotenv()





import streamlit as st
import pandas as pd

# Temporary user storage (can be replaced with CSV or DB later)
# Initialize session variables
if "users" not in st.session_state:
    st.session_state["users"] = {}   # store users

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["current_user"] = None


# ------------------ REGISTER PAGE ------------------
def register_page():
    st.title("Register")
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")

    if st.button("Create Account"):
        if username in st.session_state["users"]:
            st.error("Username already exists! Try another.")
        elif username == "" or password == "":
            st.warning("Please enter both username and password.")
        else:
            st.session_state["users"][username] = password
            st.success("✅ Registration successful! Please login.")
            st.session_state.page = "login"
    st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #2196F3;
                color: white;
                height: 60px;
                width: 200px;
                font-size: 20px;
                border-radius: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

    # ✅ Add a small button to go to login page
    if st.button("Already have an account? Login"):
        st.session_state.page = "login"


# ------------------ LOGIN PAGE ------------------
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in st.session_state["users"] and st.session_state["users"][username] == password:
           st.session_state["logged_in"] = True
           st.session_state["current_user"] = username

           st.success(f" Welcome, {username}!")
           st.session_state.page = "main"
        else:
            st.error("Incorrect username or password!")
    if st.button("Create an account? Register"):
        st.session_state.page = "register"
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                height: 60px;
                width: 200px;
                font-size: 20px;
                border-radius: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

# ------------------ FRONT PAGE ------------------
import streamlit as st
import os

def front_page():
    st.title("🚀 Welcome to AI Interview Coach")

    # Project description
    st.write("""
    **AI Interview Coach** is a smart web app designed to help students and job seekers:  
    - Practice role-specific interview questions  
    - Receive AI-generated feedback on answers  
    - Track strengths and weaknesses with easy-to-read charts  

    Improve your interview skills efficiently and confidently!
    """)

    st.write("---")  # horizontal line

    # Main banner image with safe check
    if os.path.exists("interview.jpg"):
        st.image("interview.jpg", caption="AI Interview Coach", use_container_width=True)
    else:
        st.warning("Main banner image 'interview.jpg' not found!")

    st.write("---")  # horizontal line

    # Step images with captions
    col1, col2, col3 = st.columns(3)
    with col1:
        if os.path.exists("job.png"):
            st.image("job.png", width=150)
        st.caption("Step 1: Enter Job Role")
    with col2:
        if os.path.exists("answer.png"):
            st.image("answer.png", width=150)
        st.caption("Step 2: Answer Questions")
    with col3:
        if os.path.exists("feedback.png"):
            st.image("feedback.png", width=150)
        st.caption("Step 3: Get AI Feedback")

    st.write("---")  # horizontal line
    
    st.markdown("<br>", unsafe_allow_html=True)

    # CSS for big, colorful buttons
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            height: 60px;
            width: 200px;
            font-size: 20px;
            margin: 10px;
            border-radius: 10px;
            color: white;
            background-color: #4CAF50;  /* Login button green */
        }
        div.stButton > button:last-child {
            height: 60px;
            width: 200px;
            font-size: 20px;
            margin: 10px;
            border-radius: 10px;
            color: white;
            background-color: #2196F3;  /* Register button blue */
        }
        </style>
    """, unsafe_allow_html=True)

    # Center buttons using columns
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        if st.button("Login", key="login"):
            st.session_state.page = "login"
        if st.button("Register", key="register"):
            st.session_state.page = "register"
   
   

# ------------------ MAIN INTERVIEW APP ------------------
import streamlit as st
import pandas as pd
import json

# --- Initialize session state ---
if "questions" not in st.session_state:
    st.session_state.questions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "df_results" not in st.session_state:
    st.session_state.df_results = pd.DataFrame()

def radio_with_optional_default(label, options, key):
    """
    Render a radio widget with no real default selection.
    - Tries index=None (newer Streamlit) to show nothing preselected.
    - Falls back to prepending a placeholder option for older Streamlit.
    Returns the selected option string, or None if the placeholder / no selection is chosen.
    """
    try:
        selected = st.radio(label, options=options, key=key, index=None)
        if selected == "" or selected is None:
            return None
        return selected
    except Exception:
        placeholder = "— Select an answer —"
        opts = [placeholder] + list(options)
        selected = st.radio(label, options=opts, key=key, index=0)
        return None if selected == placeholder else selected

def clear_question_keys():
    """Remove any existing question widget keys (q_*) from session_state."""
    for k in list(st.session_state.keys()):
        if k.startswith("q_"):
            del st.session_state[k]

def _extract_options_from_item(item):
    """
    Return a list of option texts in order [A, B, C, D] if possible.
    Handles several shapes:
    - item["options"] as list or dict
    - item has keys "A","B","C","D"
    - item has other enumerable option keys (we try to sort A-D or fallback to any other keys)
    """
    # 1) explicit "options" key (list or dict)
    if "options" in item:
        opts = item["options"]
        if isinstance(opts, list):
            return [str(x) for x in opts]
        if isinstance(opts, dict):
            # try to preserve A,B,C,D order if keys are letters
            letter_keys = ["A", "B", "C", "D"]
            if all(k in opts for k in letter_keys):
                return [str(opts[k]) for k in letter_keys]
            # else return values preserving insertion order
            return [str(v) for v in opts.values()]

    # 2) separate letter keys A-D
    letter_keys = ["A", "B", "C", "D"]
    if any(k in item for k in letter_keys):
        return [str(item.get(k)) for k in letter_keys if k in item]

    # 3) any other keys except "question"/"text"/"correct"
    candidates = []
    for k, v in item.items():
        if k.lower() in ("question", "text", "correct", "answer"):
            continue
        candidates.append((k, v))
    # sort by key if keys are like 'option1','option2' or '1','2'
    if candidates:
        # attempt to sort by numeric suffix or key name
        try:
            candidates.sort(key=lambda x: int(''.join(filter(str.isdigit, x[0])) or 0))
        except Exception:
            candidates.sort(key=lambda x: x[0])
        return [str(v) for (_, v) in candidates]

    # nothing usable
    return []

def _normalize_correct_answer(correct_raw, options_list):
    """
    Given the raw "correct" field and the options list, return the full option text if possible.
    Accepts:
    - full option text
    - single-letter "A"/"B"/"C"/"D" (case-insensitive)
    - index as integer or string digit
    Returns empty string if cannot determine.
    """
    if not correct_raw:
        return ""
    corr = str(correct_raw).strip()
    if corr == "":
        return ""
    # letter case
    if len(corr) == 1 and corr.upper() in "ABCD":
        idx = ord(corr.upper()) - ord("A")
        if idx < len(options_list):
            return options_list[idx]
    # numeric index (1-based)
    if corr.isdigit():
        idx = int(corr) - 1
        if 0 <= idx < len(options_list):
            return options_list[idx]
    # if exact match to an option text
    for opt in options_list:
        if corr == opt:
            return opt
    # try case-insensitive match
    for opt in options_list:
        if corr.lower() == opt.lower():
            return opt
    return ""

def _build_questions_from_parsed_json(parsed):
    """
    Accepts parsed JSON (could be dict with "questions" list, a dict of numbered items,
    or a list of items). Returns a list of question dicts with keys: question, options (list), answer (full text or empty).
    """
    questions_out = []

    items = []
    # case: top-level dict with "questions" list
    if isinstance(parsed, dict) and "questions" in parsed and isinstance(parsed["questions"], list):
        items = parsed["questions"]
    # case: top-level dict where each key is a question id mapping to object
    elif isinstance(parsed, dict):
        # check if values are objects representing questions
        # e.g., {"1": {...}, "2": {...}}
        values = list(parsed.values())
        if values and isinstance(values[0], dict) and "question" in values[0] or "text" in values[0]:
            # iterate sorted by key if keys are numeric-ish
            try:
                sorted_keys = sorted(parsed.keys(), key=lambda k: int(k) if str(k).isdigit() else k)
            except Exception:
                sorted_keys = sorted(parsed.keys())
            for k in sorted_keys:
                items.append(parsed[k])
        else:
            # otherwise maybe the dict itself describes one question
            items = [parsed]
    # case: top-level is already a list of items
    elif isinstance(parsed, list):
        items = parsed
    else:
        # unknown shape, attempt to wrap it
        items = [parsed]

    for item in items:
        if not isinstance(item, dict):
            continue
        q_text = item.get("question") or item.get("text") or ""
        options_list = _extract_options_from_item(item)
        # ensure uniqueness and trim None
        options_list = [str(o) for o in options_list if o is not None and str(o).strip() != ""]
        correct_raw = item.get("correct") or item.get("answer") or item.get("correct_answer") or item.get("Correct")
        correct_full = _normalize_correct_answer(correct_raw, options_list)
        questions_out.append({
            "question": str(q_text),
            "options": options_list,
            "answer": correct_full  # may be "" if not provided / not resolvable
        })

    return questions_out

def main_app():
    st.title("🚀 AI Interview Coach ")

    job = st.text_input("Enter job role (e.g., Data Analyst, Software Engineer)")

    # --- Generate Questions button ---
    if st.button("Generate Questions"):
        if job.strip() == "":
            st.warning("Please enter a job role first.")
        else:
            clear_question_keys()
            st.session_state.questions = []
            st.session_state.user_answers = []
            st.session_state.df_results = pd.DataFrame
            try:
                prompt = f"""
                Generate exactly 7 technical multiple-choice questions for the job role: {job}.
                Each question must have 4 options labeled A, B, C, D.
                Indicate the correct answer as the full option text.
                Return the output in strict JSON format only.
                """
                # --- API call (keep your client setup as before) ---
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw_output = response.choices[0].message.content

                # --- Parse JSON robustly ---
                parsed = json.loads(raw_output)

                questions = _build_questions_from_parsed_json(parsed)

                # If the returned questions have no options or are fewer than expected, raise a helpful error
                if not questions or any(len(q["options"]) < 2 for q in questions):
                    raise ValueError("Parsed JSON did not contain properly formatted questions/options. See RAW OUTPUT below.")

                # Clear prior widget keys and session question state
                clear_question_keys()
                st.session_state.questions = questions
                st.session_state.user_answers = []
                st.session_state.df_results = pd.DataFrame()
                

                st.success("✅ Questions generated!")

            except Exception as e:
                st.error(f"Error generating questions: {e}")
                # Show raw output to help debugging (if available)
                try:
                    st.write("RAW OUTPUT:")
                    st.code(raw_output)
                except Exception:
                    pass

    # --- Display MCQs ---
    if st.session_state.questions:
        st.header("Interview Questions")
        user_answers = []

        for i, q in enumerate(st.session_state.questions):
            st.write(f"**Q{i+1}. {q['question']}**")
            if not q["options"]:
                st.write("No options available for this question.")
                user_answers.append(None)
                continue

            selected = radio_with_optional_default(
                "Select your answer:",
                q["options"],
                key=f"q_{i}"
            )
            user_answers.append(selected)

        if st.button("Submit Answers"):
            unanswered = [i + 1 for i, ans in enumerate(user_answers) if ans is None]
            if unanswered:
                st.warning(f"Please answer all questions before submitting. Unanswered: {unanswered}")
            else:
                st.session_state.user_answers = user_answers

                scores = [
                    10 if ans == q['answer'] else 0
                    for ans, q in zip(user_answers, st.session_state.questions)
                ]
                total_score = sum(scores)
                percentage = (total_score / (len(scores) * 10)) * 100
   

                df = pd.DataFrame({
                    "Question": [q['question'] for q in st.session_state.questions],
                    "Selected Answer": user_answers,
                    "Correct Answer": [q['answer'] for q in st.session_state.questions],
                    "Score": scores
                })
                st.session_state.df_results = df

                total_score = df['Score'].sum()
                st.success(f"✅ Answers submitted! Total Score: {total_score}/{len(df) * 10}")
                st.dataframe(df)

                for i, row in df.iterrows():
                    if row["Selected Answer"] != row["Correct Answer"]:
                        st.write(f"❌ Q{i+1} - Correct Answer: {row['Correct Answer'] or 'Not provided by generator'}")
                    else:
                        st.write(f"✔️ Q{i+1} - Correct!")
    if st.button("Get AI Feedback"):
     try:
        feedback_prompt = f"""
        You are an interview coach. The candidate applied for {job}.
        Below are the questions, their answers, and correct answers.

        Provide brief, helpful feedback:
        - Strengths (based on correct answers)
        - Weaknesses or topics to improve
        - 3 actionable tips to improve interview performance.

        Data:
        {st.session_state.df_results.to_dict(orient='records')}
        """

        feedback_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": feedback_prompt}]
        )

        feedback_text = feedback_response.choices[0].message.content
        st.subheader("🧠 AI Feedback")
        st.write(feedback_text)

     except Exception as e:
        st.error(f"Error generating feedback: {e}")
    


    # --- Logout button ---
    if st.button("Logout"):
     clear_question_keys()
     st.session_state.questions = []
     st.session_state.user_answers = []
     st.session_state.df_results = pd.DataFrame()
     st.session_state.page = "front"

    # Optional: reset role input
     






# ------------------ PAGE NAVIGATION ------------------
if "page" not in st.session_state:
    st.session_state.page = "front"

if st.session_state.page == "front":
    front_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.page == "main" and st.session_state.logged_in:
    main_app()
