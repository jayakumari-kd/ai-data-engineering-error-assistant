import os
from pathlib import Path
import streamlit as st
import anthropic
import httpx2

# Claude Client
http_client = httpx2.Client(
    headers={"Accept-Encoding": "gzip, deflate"}
)

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    http_client=http_client
)

LIBRARY_PATH = Path(
    "/home/jovyan/work/Data Engineering Error Library"
)

st.title("AI Data Engineering Assistant")

error_message = st.text_area(
    "Paste Error Message",
    height=200
)

if st.button("Analyze Error"):

    matching_files = []

    for file in LIBRARY_PATH.rglob("*.md"):

        try:
            content = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            if any(
                word.lower() in content.lower()
                for word in error_message.split()
            ):
                matching_files.append((file, content))

        except Exception:
            pass

    if not matching_files:
        st.warning("No matching incidents found")
        st.stop()

    context = "\n\n".join(
        [
            f"FILE: {f.name}\n{c[:3000]}"
            for f, c in matching_files[:3]
        ]
    )

    prompt = f"""
You are a Data Engineering troubleshooting assistant.

Error:
{error_message}

Relevant incidents from Error Library:

{context}

Provide:

1. Root cause
2. Investigation steps
3. Fix recommendations
4. Similar incidents found
"""

    with st.spinner("Claude is analyzing..."):

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

    answer = "\n".join(
        block.text
        for block in response.content
        if hasattr(block, "text")
    )

    st.subheader("Claude Analysis")
    st.write(answer)

    st.subheader("Matching Files")

    for file, _ in matching_files[:3]:
        st.write(file.name)