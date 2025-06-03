import streamlit as st
import pandas as pd
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="InboxIQ", page_icon="📬", layout="wide")

st.markdown("""
<style>
    body {
        font-family: 'Inter', sans-serif;
    }
    .reportview-container .markdown-text-container {
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background-color:#F6F8FA; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
    <h1 style='color: #1F77B4;'>📬 InboxIQ</h1>
    <p style='color: #555; font-size: 16px;'>
        Track tailored resumes, summarize JDs, and write recruiter emails – all with AI.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- INIT ----------------
os.makedirs("outputs", exist_ok=True)
os.makedirs("data", exist_ok=True)
tracker_path = "outputs/application_tracker.csv"
feedback_path = "outputs/user_feedback.csv"

def load_tracker():
    if os.path.exists(tracker_path):
        return pd.read_csv(tracker_path)
    else:
        return pd.DataFrame()

# ---------------- FORM INPUTS ----------------
st.subheader("📄 Upload Job Description & Resume")

with st.form(key="input_form"):
    col1, col2 = st.columns(2)
    with col1:
        jd_file = st.file_uploader("Upload Job Description (.txt only)", type=["txt"])
        company_name = st.text_input("Company Name")
    with col2:
        resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
        job_title = st.text_input("Job Title")

    tone = st.selectbox("Tone for Email", ["Formal", "Friendly", "Bold"])
    intent = st.selectbox("Email Intent", ["Cold outreach", "Follow-up", "Thank-you"])
    submit_button = st.form_submit_button(label="🧠 Generate Summary + Email")

# ---------------- SUBMIT LOGIC ----------------
if submit_button:
    if jd_file and resume_file and company_name and job_title:
        st.success("✅ All inputs received! Generating now...")

        resume_path = f"data/{resume_file.name}"
        with open(resume_path, "wb") as f:
            f.write(resume_file.read())

        jd_text = jd_file.read().decode("utf-8")
        file_prefix = f"{company_name}_{job_title}".replace(" ", "_")
        jd_save_path = f"outputs/{file_prefix}_jd.txt"
        with open(jd_save_path, "w") as f:
            f.write(jd_text)

        summary = f"""
### 📝 JD Summary

**Key Responsibilities**:
- Define and build AI-driven product features
- Collaborate with engineering, design, and research
- Prioritize roadmap and ship at scale

**Required Skills**:
- Python, SQL, prompt engineering
- Experience with LLM APIs, Streamlit

**Ideal Candidate**:
- Product thinker with technical fluency
- Passion for building consumer-grade AI tools

**Team / Domain**:
- Gemini AI Assistant | Google Workspace
"""

        email = f"""
Hi [Recruiter],

I’m applying for the **{job_title}** role at **{company_name}**, and I believe it’s an incredible match with my background in AI-powered product design.

With 3+ years of experience building tools that leverage LLMs and personalization, and as a current MBA candidate at Cornell Tech, I’m excited to bring energy and expertise to your team.

Looking forward to connecting!

Best,  
Rumiza Shaikh
"""

        summary_path = f"outputs/{file_prefix}_summary.txt"
        email_path = f"outputs/{file_prefix}_email.txt"
        with open(summary_path, "w") as f:
            f.write(summary)
        with open(email_path, "w") as f:
            f.write(email)

        st.subheader("🧠 JD Summary")
        st.text_area("LLM-generated Job Description Summary:", summary, height=200)
        st.download_button("⬇️ Download Summary", data=open(summary_path, "rb"), file_name=os.path.basename(summary_path), mime="text/plain")

        st.subheader("📬 Recruiter Email")
        st.text_area("Email Draft to Recruiter:", email, height=200)
        st.download_button("⬇️ Download Email Draft", data=open(email_path, "rb"), file_name=os.path.basename(email_path), mime="text/plain")

        tracker_df = load_tracker()
        new_row = {
            "Company": company_name,
            "Title": job_title,
            "Status": "Applied",
            "Resume Version": resume_file.name,
            "Summary File": os.path.basename(summary_path),
            "Email File": os.path.basename(email_path)
        }
        tracker_df = pd.concat([tracker_df, pd.DataFrame([new_row])], ignore_index=True)
        tracker_df.to_csv(tracker_path, index=False)
        st.success("✅ Tracker updated and files saved successfully!")

# ---------------- DISPLAY TRACKER ----------------
st.subheader("📊 Job Application Tracker")
tracker_df = load_tracker()
if not tracker_df.empty:
    st.dataframe(tracker_df, use_container_width=True)
else:
    st.info("No job applications tracked yet. Start by submitting one above!")

# ---------------- STATUS DROPDOWN ----------------
st.subheader("🟢 Update Job Status")
if not tracker_df.empty:
    for index, row in tracker_df.iterrows():
        col1, col2 = st.columns([2, 2])
        with col1:
            st.markdown(f"**{row['Company']} – {row['Title']}**")
        with col2:
            new_status = st.selectbox(
                f"Update Status (row {index})",
                options=["Applied", "Interviewing", "Offer", "Rejected"],
                index=["Applied", "Interviewing", "Offer", "Rejected"].index(row["Status"]),
                key=f"status_{index}"
            )
            if new_status != row["Status"]:
                tracker_df.at[index, "Status"] = new_status
                st.success(f"✅ Updated: {row['Company']} – {row['Title']} → {new_status}")
    tracker_df.to_csv(tracker_path, index=False)

# ---------------- USER REVIEWS SECTION ----------------
st.subheader("⭐ Share Your Feedback")

with st.form(key="feedback_form"):
    reviewer_name = st.text_input("Your Name (Optional)")
    user_role = st.selectbox("I am a...", ["Job Seeker", "Recruiter", "Other"])
    rating = st.slider("How would you rate InboxIQ?", 1, 5, value=5)
    comment = st.text_area("Leave a comment")
    submit_feedback = st.form_submit_button("Submit Feedback")

if submit_feedback:
    feedback_df = pd.DataFrame([{
        "Name": reviewer_name,
        "Role": user_role,
        "Rating": rating,
        "Comment": comment
    }])

    if os.path.exists(feedback_path):
        existing_df = pd.read_csv(feedback_path)
        feedback_df = pd.concat([existing_df, feedback_df], ignore_index=True)

    feedback_df.to_csv(feedback_path, index=False)
    st.success("✅ Thank you for your feedback!")

# ---------------- DISPLAY FEEDBACK ----------------
st.subheader("💬 What Users Are Saying")

if os.path.exists(feedback_path):
    reviews_df = pd.read_csv(feedback_path)
    for _, row in reviews_df.tail(5).iterrows():
        st.markdown(f"**A {row['Role'].lower()} says:**")
        st.markdown(f"“{row['Comment']}”")
        st.markdown(f"⭐ {row['Rating']}/5")
        st.markdown("---")
else:
    st.info("No reviews yet — be the first to share feedback!")
