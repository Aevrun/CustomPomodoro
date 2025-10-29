# pomodoro.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time

st.set_page_config(page_title="Pomodoro + Time Tracker", layout="centered")
st.title("🍅 Pomodoro + Time Tracker")

DATA_FILE = "pomodoro_data.csv"
SOUND_FILE = "alarm.mp3"  # <-- set this to your local mp3 filename

# --- Load saved data ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=["Start", "End"])
else:
    df = pd.DataFrame(columns=["Subject", "Start", "End", "Minutes"])

# --- Helpers ---
def play_sound():
    """Play a local mp3 sound if present; otherwise show a hint."""
    if os.path.exists(SOUND_FILE):
        with open(SOUND_FILE, "rb") as f:
            st.audio(f.read(), format="audio/mp3", autoplay=True)
    else:
        st.info(f"Sound file not found: **{SOUND_FILE}**. "
                f"Place your MP3 next to pomodoro.py or update SOUND_FILE.")

# --- Initialize session state ---
ss = st.session_state
for k, v in {
    "running": False,
    "subject": "",
    "end_time": None,
    "start_time": None,
    "work_minutes": 25,
    "break_minutes": 5,
    "just_finished": False,  # shows completion screen + plays sound
}.items():
    if k not in ss:
        ss[k] = v

# --- Completion screen (if a Pomodoro just ended) ---
if ss.just_finished:
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

# --- Controls (shown when NOT running) ---
if not ss.running and not ss.just_finished:
    ss.subject = st.text_input("Enter subject or skill:", value=ss.subject)
    ss.work_minutes = st.number_input("Work duration (minutes):", 1, 240, ss.work_minutes)
    ss.break_minutes = st.number_input("Break duration (minutes):", 1, 60, ss.break_minutes)

    cols = st.columns(2)
    with cols[0]:
        if st.button("Start Pomodoro", key="start_btn") and ss.subject.strip():
            ss.start_time = datetime.now()
            ss.end_time = ss.start_time + timedelta(minutes=int(ss.work_minutes))
            ss.running = True
            st.rerun()

# --- Timer view (shown when running) ---
if ss.running:
    st.write(f"Working on: **{ss.subject}** for {ss.work_minutes} minutes…")

    # Compute remaining time
    now = datetime.now()
    remaining = ss.end_time - now
    remaining_secs = max(0, int(remaining.total_seconds()))
    mins, secs = divmod(remaining_secs, 60)

    st.subheader("Time Remaining")
    st.markdown(
        f"<h1 style='margin-top:-15px;'>{mins:02d}:{secs:02d}</h1>",
        unsafe_allow_html=True,
    )
    total_secs = int(ss.work_minutes * 60)
    progress_val = 0.0 if total_secs <= 0 else (1 - (remaining_secs / total_secs))
    st.progress(progress_val)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Stop & Save", key="stop_save_btn"):
            end = datetime.now()
            mins_done = max(1, int((end - ss.start_time).total_seconds() // 60))
            new_row = pd.DataFrame([{
                "Subject": ss.subject,
                "Start": ss.start_time,
                "End": end,
                "Minutes": mins_done
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            ss.running = False
            st.success("Session saved.")
            st.rerun()

    with col2:
        if st.button("Cancel (don’t save)", key="cancel_btn"):
            ss.running = False
            st.rerun()

    # When timer hits zero → save automatically and show completion screen
    if remaining_secs == 0 and ss.running:
        end = datetime.now()
        new_row = pd.DataFrame([{
            "Subject": ss.subject,
            "Start": ss.start_time,
            "End": end,
            "Minutes": int(ss.work_minutes)
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        ss.running = False
        ss.just_finished = True
        st.rerun()
    else:
        # Tick every second
        time.sleep(1)
        st.rerun()

# --- Manual Add Form ---
st.divider()
st.subheader("➕ Add Session Manually")

with st.form("manual_entry_form"):
    manual_subject = st.text_input("Subject (e.g., Exercise, Reading, etc.)")
    manual_date = st.date_input("Date", value=datetime.now().date())
    manual_start_time = st.time_input("Start Time", value=datetime.now().time())
    manual_minutes = st.number_input("Duration (minutes)", 1, 600, 60)

    submitted = st.form_submit_button("Add Entry")
    if submitted and manual_subject.strip():
        start_dt = datetime.combine(manual_date, manual_start_time)
        end_dt = start_dt + timedelta(minutes=int(manual_minutes))

        new_row = pd.DataFrame([{
            "Subject": manual_subject,
            "Start": start_dt,
            "End": end_dt,
            "Minutes": manual_minutes
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success(f"Added {manual_minutes} minutes of **{manual_subject}**.")
        st.rerun()

# --- Summary ---
st.divider()
st.subheader("📊 Summary")
if not df.empty:
    # Today section
    today = pd.Timestamp.today().normalize()
    today_df = df[(df["Start"] >= today) & (df["Start"] < today + pd.Timedelta(days=1))]
    st.write("**Today**")
    if not today_df.empty:
        st.dataframe(today_df.tail(20))
        st.bar_chart(today_df.groupby("Subject")["Minutes"].sum())
    else:
        st.caption("No sessions yet today.")

    # 📅 Daily (last 7 days)
    st.write("### Daily Summary (last 7 days)")
    df["Date"] = df["Start"].dt.date
    last_week = df[df["Date"] >= (pd.Timestamp.today().date() - pd.Timedelta(days=6))]
    daily_totals = last_week.groupby("Date")["Minutes"].sum()
    if not daily_totals.empty:
        st.line_chart(daily_totals)
    else:
        st.caption("No data for the last 7 days.")

    # 📅 Weekly by Subject
    st.write("### Weekly Summary by Subject")
    df["Week"] = df["Start"].dt.strftime("%Y-%U")  # Year–WeekNumber
    weekly_totals = df.groupby(["Week", "Subject"])["Minutes"].sum().unstack(fill_value=0)
    if not weekly_totals.empty:
        st.bar_chart(weekly_totals)
    else:
        st.caption("No weekly data yet.")

    # All time totals
    st.write("### All Time Totals")
    totals = df.groupby("Subject")["Minutes"].sum().sort_values(ascending=False)
    st.write(totals.to_frame("Minutes"))
else:
    st.caption("No sessions saved yet.")
