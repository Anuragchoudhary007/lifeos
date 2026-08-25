from __future__ import annotations

from datetime import date, datetime, time

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import select

from app.components.metric_card import metric_card
from app.components.section import section
from app.database import get_db
from app.theme import load_theme

from backend.models.daily_log import DailyLog
from backend.models.user import User
from backend.services.study_analytics_service import StudyAnalyticsService
from backend.services.study_service import StudyService
from backend.services.subject_service import SubjectService


# =========================================================
# PAGE CONFIG
# =========================================================

load_theme()

st.title("📚 Study Dashboard")


# =========================================================
# DATABASE
# =========================================================

db = get_db()


try:

    # =====================================================
    # ANALYTICS SERVICE
    # =====================================================

    analytics = StudyAnalyticsService(db)

    today_hours = analytics.today_hours()
    week_hours = analytics.week_hours()
    month_hours = analytics.month_hours()
    streak = analytics.current_streak()


    # =====================================================
    # KPI CARDS
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Today",
            f"{today_hours:.1f}h",
        )

    with col2:
        metric_card(
            "This Week",
            f"{week_hours:.1f}h",
        )

    with col3:
        metric_card(
            "This Month",
            f"{month_hours:.1f}h",
        )

    with col4:
        metric_card(
            "Streak",
            f"{streak} Days",
        )


    st.divider()


    # =====================================================
    # MAIN LAYOUT
    # =====================================================

    left, right = st.columns([1, 1.3])


    # =====================================================
    # ADD STUDY SESSION
    # =====================================================

    with left:

        section("➕ Add Study Session")

        subjects = SubjectService(db).get_subjects()

        if not subjects:

            st.warning(
                "No subjects found. "
                "Run the subject seed script."
            )

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


            # =================================================
            # SAVE SESSION
            # =================================================

            if submitted:

                if not topic.strip():

                    st.error(
                        "Please enter a topic."
                    )

                elif end_time <= start_time:

                    st.error(
                        "End time must be after start time."
                    )

                else:

                    user = db.scalars(
                        select(User).where(
                            User.email
                            == "anurag@lifeos.local"
                        )
                    ).first()


                    if user is None:

                        st.error(
                            "LifeOS user not found. "
                            "Run: "
                            "python -m scripts.seed_user"
                        )

                    else:

                        # -------------------------------------
                        # Find Daily Log
                        # -------------------------------------

                        log = db.scalars(
                            select(DailyLog).where(
                                DailyLog.user_id == user.id,
                                DailyLog.log_date == study_date,
                            )
                        ).first()


                        # -------------------------------------
                        # Create Daily Log
                        # -------------------------------------

                        if log is None:

                            log = DailyLog(
                                user_id=user.id,
                                log_date=study_date,
                            )

                            db.add(log)
                            db.commit()
                            db.refresh(log)


                        # -------------------------------------
                        # Create Study Session
                        # -------------------------------------

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


                        st.success(
                            "✅ Study session saved!"
                        )

                        st.rerun()


    # =====================================================
    # RECENT SESSIONS
    # =====================================================

    with right:

        section("📋 Recent Sessions")

        study_service = StudyService(db)

        sessions = study_service.get_sessions()


        if not sessions:

            st.info(
                "No study sessions yet."
            )

        else:

            for session in sessions[:10]:

                focus_display = (
                    f"{session.focus_score}/10"
                    if session.focus_score is not None
                    else "N/A"
                )

                st.markdown(
                    f"""
                    **{session.topic}**

                    📚 {session.subject.name}

                    ⏱️ {session.duration_minutes} minutes

                    🎯 Focus: {focus_display}
                    """
                )

                st.divider()


    # =====================================================
    # STUDY ANALYTICS
    # =====================================================

    st.divider()

    section("📊 Study Analytics")


    # =====================================================
    # WEEKLY + SUBJECT CHARTS
    # =====================================================

    chart1, chart2 = st.columns(2)


    # -----------------------------------------------------
    # Weekly Trend
    # -----------------------------------------------------

    with chart1:

        st.subheader(
            "📈 Weekly Study Hours"
        )

        weekly = analytics.weekly_trend()

        weekly_df = pd.DataFrame(
            {
                "Day": list(weekly.keys()),
                "Hours": list(weekly.values()),
            }
        )


        fig = px.bar(
            weekly_df,
            x="Day",
            y="Hours",
            text_auto=".1f",
            title="Study Hours by Day",
        )


        fig.update_layout(
            height=350,
            margin=dict(
                l=10,
                r=10,
                t=50,
                b=10,
            ),
            xaxis_title=None,
            yaxis_title="Hours",
        )


        st.plotly_chart(
            fig,
            use_container_width=True,
        )


    # -----------------------------------------------------
    # Subject Distribution
    # -----------------------------------------------------

    with chart2:

        st.subheader(
            "📚 Subject Distribution"
        )

        subject_data = (
            analytics.subject_distribution()
        )


        if subject_data:

            subject_df = pd.DataFrame(
                {
                    "Subject": list(
                        subject_data.keys()
                    ),
                    "Hours": list(
                        subject_data.values()
                    ),
                }
            )


            fig = px.pie(
                subject_df,
                names="Subject",
                values="Hours",
                hole=0.55,
                title="Where Your Study Time Goes",
            )


            fig.update_layout(
                height=350,
                margin=dict(
                    l=10,
                    r=10,
                    t=50,
                    b=10,
                ),
            )


            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:

            st.info(
                "No study data yet."
            )


    # =====================================================
    # FOCUS TREND
    # =====================================================

    st.subheader(
        "🎯 Focus Score Trend"
    )

    focus_data = analytics.focus_trend()


    if focus_data:

        focus_df = pd.DataFrame(
            {
                "Date": list(
                    focus_data.keys()
                ),
                "Focus": list(
                    focus_data.values()
                ),
            }
        )


        fig = px.line(
            focus_df,
            x="Date",
            y="Focus",
            markers=True,
            title="Average Focus Score",
        )


        fig.update_yaxes(
            range=[0, 10]
        )


        fig.update_layout(
            height=350,
            margin=dict(
                l=10,
                r=10,
                t=50,
                b=10,
            ),
            yaxis_title="Focus / 10",
        )


        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No focus data yet."
        )


finally:

    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    db.close()