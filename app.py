import os
from pathlib import Path

import anthropic
import httpx2
import streamlit as st


# ==========================================
# CONFIG
# ==========================================

LIBRARY_PATH = Path(
    "/home/jovyan/work/Data Engineering Error Library"
)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# ==========================================
# CLAUDE CLIENT
# ==========================================

http_client = httpx2.Client(
    headers={
        "Accept-Encoding": "gzip, deflate"
    }
)

client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    http_client=http_client
)

# ==========================================
# STREAMLIT UI
# ==========================================

st.set_page_config(
    page_title="AI Data Engineering Assistant",
    layout="wide"
)

st.title("🚀 AI Data Engineering Assistant")

st.write(
    "Paste an error message and search your Error Library."
)

error_message = st.text_area(
    "Paste Error Message",
    height=200,
    placeholder="java.lang.OutOfMemoryError: Java heap space"
)

# ==========================================
# SEARCH FUNCTION
# ==========================================

def find_matching_files(error_text):

    matches = []

    keywords = [
        word.lower()
        for word in error_text.split()
        if len(word) > 3
    ]

    for file in LIBRARY_PATH.rglob("*.md"):

        try:

            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            score = 0

            for keyword in keywords:
                score += content.lower().count(keyword)

            if score > 0:
                matches.append(
                    {
                        "file": file,
                        "content": content,
                        "score": score
                    }
                )

        except Exception:
            pass

    matches = sorted(
        matches,
        key=lambda x: x["score"],
        reverse=True
    )

    return matches[:5]


# ==========================================
# ANALYZE BUTTON
# ==========================================

if st.button("Analyze Error"):

    if not error_message.strip():

        st.warning("Please enter an error message.")

    else:

        with st.spinner("Searching Error Library..."):

            matches = find_matching_files(
                error_message
            )

        if not matches:

            st.error(
                "No matching incidents found."
            )

        else:

            st.subheader("📚 Matching Incidents")

            for match in matches:

                st.write(
                    f"✅ {match['file'].name}"
                )

            context = "\n\n".join(
                [
                    f"""
FILE: {m['file'].name}

CONTENT:
{m['content'][:4000]}
"""
                    for m in matches[:3]
                ]
            )

            prompt = f"""
You are a senior Data Engineering troubleshooting assistant.

USER ERROR:

{error_message}

RELEVANT INCIDENTS FROM ERROR LIBRARY:

{context}

Tasks:

1. Identify likely root cause
2. Explain investigation steps
3. Suggest fixes
4. Mention which incidents are most relevant
5. Recommend Spark/Kubernetes/SQL tuning if applicable
6. Give confidence level

Separate:
- Findings from Error Library
- General Engineering Knowledge
"""

            with st.spinner(
                "Claude is analyzing..."
            ):

                response = client.messages.create(
                    model="claude-sonnet-5",
                    max_tokens=1500,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

            answer_parts = []

            for block in response.content:

                if hasattr(block, "text"):
                    answer_parts.append(
                        block.text
                    )

            answer = "\n".join(answer_parts)

            st.subheader(
                "🤖 Claude Analysis"
            )

            st.markdown(answer)