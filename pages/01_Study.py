from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st
from sqlalchemy import select

from app.components.metric_card import metric_card
from app.components.section import section
from app.database import get_db
from app.theme import load_theme

from backend.models.daily_log import DailyLog
from backend.models.user import User
from backend.services.study_service import StudyService
from backend.services.subject_service import SubjectService


load_theme()

st.title("📚 Study Dashboard")

# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

db = get_db()

# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card("Today", "0h")

with col2:
    metric_card("This Week", "0h")

with col3:
    metric_card("This Month", "0h")

with col4:
    metric_card("Streak", "0 Days")

st.divider()

# ---------------------------------------------------------
# Main Layout
# ---------------------------------------------------------

left, right = st.columns([1, 1.3])

# =========================================================
# ADD STUDY SESSION
# =========================================================

with left:

    section("➕ Add Study Session")

    subjects = SubjectService(db).get_subjects()

    if not subjects:
        st.warning("No subjects found. Run the subject seed script.")
    else:

        with st.form("study_form"):

            subject = st.selectbox(
                "Subject",
                subjects,
                format_func=lambda s: s.name,
            )

            topic = st.text_input(
                "Topic",
                placeholder="e.g. SQL JOINs",
            )

            study_date = st.date_input(
                "Date",
                value=date.today(),
            )

            start_time = st.time_input(
                "Start Time",
                value=time(9, 0),
            )

            end_time = st.time_input(
                "End Time",
                value=time(10, 0),
            )

            focus = st.slider(
                "Focus Score",
                min_value=1,
                max_value=10,
                value=8,
            )

            notes = st.text_area(
                "Notes",
                placeholder="What did you learn?",
            )

            submitted = st.form_submit_button(
                "💾 Save Session",
                use_container_width=True,
            )

        # -------------------------------------------------
        # SAVE SESSION
        # -------------------------------------------------

        if submitted:

            if not topic.strip():
                st.error("Please enter a topic.")

            elif end_time <= start_time:
                st.error("End time must be after start time.")

            else:

                user = db.scalars(
                    select(User).where(
                        User.email == "anurag@lifeos.local"
                    )
                ).first()

                if user is None:

                    st.error(
                        "LifeOS user not found. "
                        "Run: python -m scripts.seed_user"
                    )

                else:

                    # Find today's DailyLog
                    log = db.scalars(
                        select(DailyLog).where(
                            DailyLog.user_id == user.id,
                            DailyLog.log_date == study_date,
                        )
                    ).first()

                    # Create DailyLog if it doesn't exist
                    if log is None:

                        log = DailyLog(
                            user_id=user.id,
                            log_date=study_date,
                        )

                        db.add(log)
                        db.commit()
                        db.refresh(log)

                    # Create study session
                    service = StudyService(db)

                    service.create_session(
                        daily_log_id=log.id,
                        subject_id=subject.id,
                        topic=topic.strip(),
                        started_at=datetime.combine(
                            study_date,
                            start_time,
                        ),
                        ended_at=datetime.combine(
                            study_date,
                            end_time,
                        ),
                        focus_score=focus,
                        notes=notes.strip() or None,
                    )

                    st.success("✅ Study session saved!")

                    st.rerun()


# =========================================================
# RECENT SESSIONS
# =========================================================

with right:

    section("📋 Recent Sessions")

    study_service = StudyService(db)
    sessions = study_service.get_sessions()

    if not sessions:

        st.info("No study sessions yet.")

    else:

        for session in sessions[:10]:

            st.markdown(
                f"""
                **{session.topic}**

                📚 {session.subject.name}  
                ⏱️ {session.duration_minutes} minutes  
                🎯 Focus: {session.focus_score}/10
                """
            )

            st.divider()


# ---------------------------------------------------------
# Close database
# ---------------------------------------------------------

db.close()