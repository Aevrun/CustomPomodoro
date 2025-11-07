# pomodoro.py — Enhanced Version
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="🍅 Pomodoro + Time Tracker", layout="centered")
st.title("🍅 Pomodoro + Time Tracker")

DATA_FILE = "pomodoro_data.csv"
CATEGORY_FILE = "categories.txt"
SOUND_FILE = "alarm.mp3"

# -------------------- LOAD DATA --------------------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=["Start", "End"])
else:
    df = pd.DataFrame(columns=["Subject", "Start", "End", "Minutes"])

# Ensure extra editable columns exist
extra_cols = ["Category", "Notes", "Summary", "Action"]
for col in extra_cols:
    if col not in df.columns:
        df[col] = ""

# -------------------- HELPERS --------------------
def play_sound():
    """Play local mp3 if present, otherwise hint."""
    if os.path.exists(SOUND_FILE):
        with open(SOUND_FILE, "rb") as f:
            st.audio(f.read(), format="audio/mp3", autoplay=True)
    else:
        st.info(f"Sound file not found: **{SOUND_FILE}**")

def update_page_title():
    """Update the browser tab title with live countdown."""
    if ss.get("running", False) and ss.get("end_time"):
        remaining = ss.end_time - datetime.now()
        mins, secs = divmod(max(0, int(remaining.total_seconds())), 60)
        st.set_page_config(page_title=f"⏰ {mins:02d}:{secs:02d} left | Pomodoro Tracker")
    else:
        st.set_page_config(page_title="🍅 Pomodoro + Time Tracker")

# -------------------- SESSION STATE --------------------
ss = st.session_state
for k, v in {
    "running": False,
    "subject": "",
    "category": "",
    "end_time": None,
    "start_time": None,
    "work_minutes": 25,
    "break_minutes": 5,
    "just_finished": False,
    "paused": False,
    "remaining_secs": None,
}.items():
    if k not in ss:
        ss[k] = v

update_page_title()

# -------------------- COMPLETION SCREEN --------------------
if ss.just_finished:
    # MODIFICATION 2: Only show completion screen if just finished
    st.success("✅ Pomodoro complete and saved!")
    play_sound()
    st.balloons()
    col_ok, col_start_break = st.columns(2)
    with col_ok:
        if st.button("OK", key="dismiss_finish"):
            ss.just_finished = False
            st.rerun()
    with col_start_break:
        if st.button("Start Break (5 min)", key="start_break_btn"):
            ss.subject = "Break"
            ss.work_minutes = ss.break_minutes
            ss.start_time = datetime.now()
            ss.end_time = ss.start_time + timedelta(minutes=int(ss.work_minutes))
            ss.running = True
            ss.just_finished = False
            st.rerun()
    st.divider()

# MODIFICATION 2: Wrap all non-timer elements in this 'if' block
if not ss.running and not ss.just_finished:
    # -------------------- CATEGORY MANAGEMENT --------------------
    if os.path.exists(CATEGORY_FILE):
        with open(CATEGORY_FILE) as f:
            categories = [line.strip() for line in f if line.strip()]
    else:
        categories = []

    st.write("### 🗂️ Categories")
    new_cat = st.text_input("Add new category:")
    if st.button("Add Category") and new_cat.strip():
        categories.append(new_cat.strip())
        with open(CATEGORY_FILE, "w") as f:
            f.write("\n".join(sorted(set(categories))))
        st.success("Category added!")
        st.rerun()

    # The rest of the Category section (moved inside the 'if' block)
    selected_cat = st.selectbox("Select Category (optional):", [""] + categories)
    ss.category = selected_cat

    # -------------------- MAIN CONTROLS --------------------
    ss.subject = st.text_input("Enter subject or skill:", value=ss.subject)
    ss.work_minutes = st.number_input("Work duration (minutes):", 1, 240, ss.work_minutes)
    ss.break_minutes = st.number_input("Break duration (minutes):", 1, 60, ss.break_minutes)

    cols = st.columns(2)
    with cols[0]:
        # Changed condition to use ss.category instead of ss.subject if a category is selected
        if st.button("Start Pomodoro", key="start_btn") and (ss.subject.strip() or ss.category.strip()):
            ss.start_time = datetime.now()
            ss.end_time = ss.start_time + timedelta(minutes=int(ss.work_minutes))
            ss.running = True
            st.rerun()

# -------------------- TIMER VIEW --------------------
if ss.running:
    # This section is kept outside the 'if not ss.running' block so it always displays when running.
    st.write(f"Working on: **{ss.subject}** ({ss.category}) for {ss.work_minutes} minutes…")

    now = datetime.now()
    if ss.paused:
        remaining_secs = ss.remaining_secs
    else:
        remaining = ss.end_time - now
        remaining_secs = max(0, int(remaining.total_seconds()))
        ss.remaining_secs = remaining_secs

    mins, secs = divmod(remaining_secs, 60)
    st.subheader("Time Remaining")
    st.markdown(f"<h1 style='margin-top:-15px;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)

    total_secs = int(ss.work_minutes * 60)
    progress_val = 0.0 if total_secs <= 0 else (1 - (remaining_secs / total_secs))
    st.progress(progress_val)

    col1, col2, col3 = st.columns(3)
    with col1:
        if ss.paused:
            if st.button("Resume"):
                ss.paused = False
                ss.start_time = datetime.now()
                ss.end_time = ss.start_time + timedelta(seconds=ss.remaining_secs)
                st.rerun()
        else:
            if st.button("Pause"):
                ss.paused = True
                st.rerun()

    with col2:
        if st.button("Stop & Save", key="stop_save_btn"):
            end = datetime.now()
            mins_done = max(1, int((end - ss.start_time).total_seconds() // 60))
            new_row = pd.DataFrame([{
                "Subject": ss.subject,
                "Category": ss.category,
                "Start": ss.start_time,
                "End": end,
                "Minutes": mins_done,
                "Notes": "",
                "Summary": "",
                "Action": ""
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            ss.running = False
            ss.paused = False
            st.success("Session saved.")
            st.rerun()

    with col3:
        if st.button("Cancel (don’t save)", key="cancel_btn"):
            ss.running = False
            ss.paused = False
            st.rerun()

    if remaining_secs == 0 and ss.running and not ss.paused:
        end = datetime.now()
        new_row = pd.DataFrame([{
            "Subject": ss.subject,
            "Category": ss.category,
            "Start": ss.start_time,
            "End": end,
            "Minutes": int(ss.work_minutes),
            "Notes": "",
            "Summary": "",
            "Action": ""
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        ss.running = False
        ss.just_finished = True
        st.rerun()

    if not ss.paused:
        time.sleep(1)
        st.rerun()

# MODIFICATION 2: Wrap all non-timer elements in this 'if' block
if not ss.running and not ss.just_finished:
    # -------------------- MANUAL ADD FORM --------------------
    st.divider()
    st.subheader("➕ Add Session Manually")

    with st.form("manual_entry_form"):
        manual_subject = st.text_input("Subject:")
        manual_category = st.selectbox("Category:", [""] + categories)
        manual_date = st.date_input("Date", value=datetime.now().date())
        manual_start_time = st.time_input("Start Time", value=datetime.now().time())
        manual_minutes = st.number_input("Duration (minutes)", 1, 600, 60)
        submitted = st.form_submit_button("Add Entry")

        if submitted and manual_subject.strip():
            start_dt = datetime.combine(manual_date, manual_start_time)
            end_dt = start_dt + timedelta(minutes=int(manual_minutes))
            new_row = pd.DataFrame([{
                "Subject": manual_subject,
                "Category": manual_category,
                "Start": start_dt,
                "End": end_dt,
                "Minutes": manual_minutes,
                "Notes": "",
                "Summary": "",
                "Action": ""
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Added {manual_minutes} minutes of **{manual_subject}**.")
            st.rerun()

    # -------------------- EDITABLE TABLE --------------------
    st.divider()
    st.subheader("✏️ Edit Entries")
    if not df.empty:
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Save Changes"):
            edited_df.to_csv(DATA_FILE, index=False)
            st.success("Changes saved.")
            st.rerun()

    # -------------------- SUMMARY --------------------
    st.divider()
    st.subheader("📊 Summary")
    if not df.empty:
        df["Date"] = df["Start"].dt.date
        today = pd.Timestamp.today().normalize()
        today_df = df[(df["Start"] >= today) & (df["Start"] < today + pd.Timedelta(days=1))]
        st.write("**Today**")
        if not today_df.empty:
            st.dataframe(today_df.tail(20))
            # MODIFICATION 1: Change to group by Category
            st.bar_chart(today_df.groupby("Category")["Minutes"].sum())
        else:
            st.caption("No sessions yet today.")

        st.write("### Daily Summary (last 7 days)")
        last_week = df[df["Date"] >= (pd.Timestamp.today().date() - pd.Timedelta(days=6))]
        daily_totals = last_week.groupby("Date")["Minutes"].sum()
        if not daily_totals.empty:
            st.line_chart(daily_totals)
        else:
            st.caption("No data for the last 7 days.")

        st.write("### Weekly Summary by Category")
        df["Week"] = df["Start"].dt.strftime("%Y-%U")
        # MODIFICATION 1: Change to group by Category
        weekly_totals = df.groupby(["Week", "Category"])["Minutes"].sum().unstack(fill_value=0)
        if not weekly_totals.empty:
            st.bar_chart(weekly_totals)
        else:
            st.caption("No weekly data yet.")

        st.write("### All Time Totals")
        # MODIFICATION 1: Change to group by Category
        totals = df.groupby(["Category"])["Minutes"].sum().sort_values(ascending=False)
        st.write(totals.to_frame("Minutes"))
    else:
        st.caption("No sessions saved yet.")