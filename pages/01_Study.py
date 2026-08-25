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
from backend.services.study_advanced_analytics import (
    AdvancedStudyAnalytics,
)
from backend.services.study_goal_service import StudyGoalService
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
    goal_service = StudyGoalService(analytics)

    sessions = analytics.get_sessions()

    advanced = AdvancedStudyAnalytics(sessions)

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

    section("🎯 Weekly Study Goal")

    goal_col1, goal_col2 = st.columns([1, 2])

    with goal_col1:

        weekly_target = st.number_input(
            "Weekly Target (hours)",
            min_value=1.0,
            max_value=168.0,
            value=20.0,
            step=1.0,
        )

    with goal_col2:

        goal = goal_service.weekly_progress(
            weekly_target
        )

        st.metric(
            "Weekly Progress",
            f"{goal['actual']:.1f} / {goal['target']:.1f} h",
        )

        st.progress(
            goal["progress"],
            text=(
                f"{goal['progress'] * 100:.1f}% "
                f"complete"
            ),
        )

        if goal["remaining"] > 0:

            st.caption(
                f"⏳ {goal['remaining']:.1f}h remaining"
            )

        else:

            st.success(
                "🏆 Weekly study goal completed!"
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

    st.divider()

    section("🔬 Advanced Productivity Analysis")

    advanced_col1, advanced_col2 = st.columns(2)


    # =========================================================
    # WEEKDAY PRODUCTIVITY
    # =========================================================

    with advanced_col1:

        st.subheader("📆 Study Hours by Weekday")

        weekday_data = advanced.weekday_hours()

        weekday_df = pd.DataFrame(
            {
                "Weekday": list(weekday_data.keys()),
                "Hours": list(weekday_data.values()),
            }
        )

        fig = px.bar(
            weekday_df,
            x="Weekday",
            y="Hours",
            title="Which Days Are Most Productive?",
            text_auto=".1f",
        )

        fig.update_layout(
            height=380,
            xaxis_title=None,
            yaxis_title="Hours",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


    # =========================================================
    # BEST STUDY TIME
    # =========================================================

    with advanced_col2:

        st.subheader("⏰ Study Time Distribution")

        hourly_data = advanced.hourly_distribution()

        if hourly_data:

            hourly_df = pd.DataFrame(
                {
                    "Hour": list(hourly_data.keys()),
                    "Hours": list(hourly_data.values()),
                }
            )

            hourly_df["Time"] = hourly_df["Hour"].apply(
                lambda x: f"{x:02d}:00"
            )

            fig = px.bar(
                hourly_df,
                x="Time",
                y="Hours",
                title="When You Study Most",
                text_auto=".1f",
            )

            fig.update_layout(
                height=380,
                xaxis_title="Start Time",
                yaxis_title="Hours",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:

            st.info("No study data yet.")

    # =========================================================
    # 7-DAY ROLLING AVERAGE
    # =========================================================

    st.subheader("📈 7-Day Rolling Study Average")

    rolling = advanced.rolling_7_day_average()

    if rolling:

        rolling_df = pd.DataFrame(
            rolling,
            columns=["Date", "Average"],
        )

        fig = px.line(
            rolling_df,
            x="Date",
            y="Average",
            markers=True,
            title="7-Day Rolling Average",
        )

        fig.update_layout(
            height=380,
            yaxis_title="Average Hours / Day",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info("Not enough study data yet.")

    # =========================================================
    # STUDY ACTIVITY HEATMAP
    # =========================================================

    st.subheader("📅 Study Activity")

    daily = advanced.daily_hours()

    if daily:

        heatmap_df = pd.DataFrame(
            {
                "Date": list(daily.keys()),
                "Hours": list(daily.values()),
            }
        )

        fig = px.density_heatmap(
            heatmap_df,
            x="Date",
            y=["Study"] * len(heatmap_df),
            z="Hours",
            histfunc="sum",
            title="Study Activity Heatmap",
        )

        fig.update_layout(
            height=220,
            xaxis_title=None,
            yaxis_title=None,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info("No study activity yet.")

    st.divider()

    section("🎯 Performance Overview")

    total_hours = advanced.total_hours()
    average_focus = advanced.average_focus()
    consistency = advanced.consistency_score()

    performance_col1, performance_col2, performance_col3 = st.columns(3)

    with performance_col1:
        metric_card(
            "Total Study",
            f"{total_hours:.1f}h",
        )

    with performance_col2:
        metric_card(
            "Average Focus",
            f"{average_focus:.1f}/10",
        )

    with performance_col3:
        metric_card(
            "Consistency",
            f"{consistency:.0f}%",
        )

    st.subheader("🏆 Subject Performance")

    performance = advanced.subject_performance()

    if performance:

        performance_df = pd.DataFrame(performance)

        st.dataframe(
            performance_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No subject performance data yet.")

    st.subheader("🧠 Focus vs Study Duration")

    if sessions:

        scatter_df = pd.DataFrame(
            [
                {
                    "Subject": session.subject.name,
                    "Duration": session.duration_minutes,
                    "Focus": session.focus_score,
                    "Topic": session.topic,
                }
                for session in sessions
                if session.focus_score is not None
            ]
        )

        if not scatter_df.empty:

            fig = px.scatter(
                scatter_df,
                x="Duration",
                y="Focus",
                color="Subject",
                hover_data=["Topic"],
                title="Does Longer Study Mean Better Focus?",
            )

            fig.update_layout(
                height=400,
                xaxis_title="Study Duration (minutes)",
                yaxis_title="Focus Score",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:

            st.info(
                "Add focus scores to your sessions "
                "to see this analysis."
            )

    else:

        st.info("No study sessions yet.")


finally:

    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    db.close()