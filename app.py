"""
Ownership Log — Streamlit v3.4
نسخه نهایی — جستجوی قطعی + Checkbox
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# تنظیمات
# ============================================================
st.set_page_config(
    page_title="Ownership Log — v3.4",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    textarea {
        font-size: 24px !important;
        line-height: 1.6 !important;
    }
    input[type="text"],
    input[type="number"] {
        font-size: 24px !important;
        line-height: 1.6 !important;
    }
    textarea::placeholder,
    input::placeholder {
        font-size: 24px !important;
        opacity: 0.5 !important;
    }
    label {
        font-size: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
LOG_FILE = DATA_DIR / "ownership_log.csv"
TOTAL_DAYS = 640
START_DATE = datetime(2026, 9, 17).date()

# ============================================================
# توابع کمکی
# ============================================================
def get_semester_week(day):
    semester = (day - 1) // 80 + 1
    week_in_sem = ((day - 1) % 80) // 5 + 1
    return f"S{semester}/W{week_in_sem}"

def get_date(day):
    return START_DATE + timedelta(days=day - 1)

def is_empty(val):
    if pd.isna(val):
        return True
    s = str(val).strip().lower()
    return s in ["", "nan", "none", "null"]

def is_day_filled(row):
    eco = row.get("① Economic", 0)
    eco_filled = False
    if not is_empty(eco):
        try:
            eco_filled = float(eco) > 0
        except:
            pass
    ctrl_filled = not is_empty(row.get("② Control", ""))
    trans_filled = not is_empty(row.get("③ Transferable", ""))
    dep_filled = not is_empty(row.get("④ Dependence", ""))
    return eco_filled or ctrl_filled or trans_filled or dep_filled

def is_day_complete(row):
    eco = row.get("① Economic", 0)
    eco_ok = False
    if not is_empty(eco):
        try:
            eco_ok = float(eco) > 0
        except:
            pass
    return (eco_ok and 
            not is_empty(row.get("② Control", "")) and
            not is_empty(row.get("③ Transferable", "")) and
            not is_empty(row.get("④ Dependence", "")))

def create_empty_log():
    rows = []
    for day in range(1, TOTAL_DAYS + 1):
        rows.append({
            "روز": day,
            "تاریخ": get_date(day).strftime("%Y-%m-%d"),
            "سمستر/هفته": get_semester_week(day),
            "① Economic": 0,
            "② Control": "",
            "③ Transferable": "",
            "④ Dependence": "",
            "یادداشت": ""
        })
    return pd.DataFrame(rows)

def save_log(df):
    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")

def load_log():
    if LOG_FILE.exists():
        try:
            df = pd.read_csv(LOG_FILE, encoding="utf-8-sig")
            required = ["روز", "تاریخ", "سمستر/هفته", "① Economic", 
                       "② Control", "③ Transferable", "④ Dependence", "یادداشت"]
            if not all(c in df.columns for c in required):
                df = create_empty_log()
                save_log(df)
                return df
            
            df["روز"] = pd.to_numeric(df["روز"], errors="coerce").fillna(0).astype(int)
            
            if len(df) < TOTAL_DAYS:
                existing = set(df["روز"].tolist())
                new_rows = []
                for day in range(1, TOTAL_DAYS + 1):
                    if day not in existing:
                        new_rows.append({
                            "روز": day,
                            "تاریخ": get_date(day).strftime("%Y-%m-%d"),
                            "سمستر/هفته": get_semester_week(day),
                            "① Economic": 0,
                            "② Control": "",
                            "③ Transferable": "",
                            "④ Dependence": "",
                            "یادداشت": ""
                        })
                if new_rows:
                    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                    df = df.sort_values("روز").reset_index(drop=True)
                    save_log(df)
            for col in ["② Control", "③ Transferable", "④ Dependence", "یادداشت"]:
                df[col] = df[col].fillna("")
            df["① Economic"] = df["① Economic"].fillna(0)
            return df
        except Exception as e:
            st.error(f"خطا: {e}")
            df = create_empty_log()
            save_log(df)
            return df
    else:
        df = create_empty_log()
        save_log(df)
        return df

def get_current_day(df):
    for idx, row in df.iterrows():
        if not is_day_filled(row):
            return int(row["روز"]), idx
    return None, None

def render_big_day(row, day_num):
    """نمایش بزرگ یک روز"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #1F4E78, #2E75B6);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin: 20px 0;
    ">
        <h2 style="margin: 0; color: white; font-size: 32px;">
            📅 روز {day_num}
        </h2>
        <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 22px;">
            {row['سمستر/هفته']} — {row['تاریخ']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: #E8F5E9;
            padding: 25px;
            border-radius: 12px;
            border-left: 6px solid #4CAF50;
            margin-bottom: 15px;
        ">
            <div style="font-size: 24px; color: #2E7D32; font-weight: bold; margin-bottom: 10px;">
                💰 Economic Ownership
            </div>
            <div style="font-size: 36px; color: #1B5E20; font-weight: bold;">
                ${row['① Economic']:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        ctrl_text = row["② Control"] if not is_empty(row["② Control"]) else "—"
        st.markdown(f"""
        <div style="
            background: #E3F2FD;
            padding: 25px;
            border-radius: 12px;
            border-left: 6px solid #2196F3;
            margin-bottom: 15px;
        ">
            <div style="font-size: 24px; color: #1565C0; font-weight: bold; margin-bottom: 10px;">
                🎯 Control / Rights
            </div>
            <div style="font-size: 24px; color: #0D47A1; line-height: 1.8;">
                {ctrl_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        trans_text = row["③ Transferable"] if not is_empty(row["③ Transferable"]) else "—"
        st.markdown(f"""
        <div style="
            background: #F3E5F5;
            padding: 25px;
            border-radius: 12px;
            border-left: 6px solid #9C27B0;
            margin-bottom: 15px;
        ">
            <div style="font-size: 24px; color: #6A1B9A; font-weight: bold; margin-bottom: 10px;">
                📦 Transferable Asset
            </div>
            <div style="font-size: 24px; color: #4A148C; line-height: 1.8;">
                {trans_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        dep_text = row["④ Dependence"] if not is_empty(row["④ Dependence"]) else "—"
        st.markdown(f"""
        <div style="
            background: #FFF3E0;
            padding: 25px;
            border-radius: 12px;
            border-left: 6px solid #FF9800;
            margin-bottom: 15px;
        ">
            <div style="font-size: 24px; color: #E65100; font-weight: bold; margin-bottom: 10px;">
                📋 Reduced Dependence
            </div>
            <div style="font-size: 24px; color: #BF360C; line-height: 1.8;">
                {dep_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if not is_empty(row.get("یادداشت", "")):
        st.markdown(f"""
        <div style="
            background: #FAFAFA;
            padding: 20px;
            border-radius: 12px;
            border: 2px dashed #CCC;
            margin-top: 15px;
        ">
            <div style="font-size: 24px; color: #666; font-weight: bold; margin-bottom: 10px;">
                📝 یادداشت
            </div>
            <div style="font-size: 24px; color: #333; line-height: 1.8;">
                {row['یادداشت']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# بارگذاری
# ============================================================
df = load_log()

# ============================================================
# State
# ============================================================
if "page" not in st.session_state:
    st.session_state["page"] = "📅 امروز"

if "expanded_day" not in st.session_state:
    st.session_state["expanded_day"] = None

if "search_result" not in st.session_state:
    st.session_state["search_result"] = None

if "edit_day_input" not in st.session_state:
    today_day, _ = get_current_day(df)
    st.session_state["edit_day_input"] = int(today_day) if today_day else 1

# ============================================================
# Sidebar
# ============================================================
st.sidebar.title("📊 Ownership Log")
st.sidebar.caption("v3.4")

pages = ["📅 امروز", "📋 Log کامل", "📈 Dashboard", "🎯 Checkpoint", "📖 راهنما"]

selected_page = st.sidebar.radio(
    "برو به:",
    pages,
    index=pages.index(st.session_state["page"]) if st.session_state["page"] in pages else 0
)

if selected_page != st.session_state["page"]:
    st.session_state["page"] = selected_page

page = st.session_state["page"]

filled_count = sum(1 for _, r in df.iterrows() if is_day_filled(r))
complete_count = sum(1 for _, r in df.iterrows() if is_day_complete(r))

st.sidebar.divider()
st.sidebar.metric("روزهای پر", filled_count)
st.sidebar.metric("روزهای کامل", complete_count)
st.sidebar.metric("کل", TOTAL_DAYS)

# ============================================================
# صفحه ۱: امروز
# ============================================================
if page == "📅 امروز":
    st.title("📅 ثبت امروز")
    st.caption("بعد از هر جلسه → ۳ دقیقه پر کن → تمام")

    today_day, today_row_idx = get_current_day(df)
    
    if today_day is None:
        st.info("🎉 همه روزها پر شده")
        today_day = TOTAL_DAYS
    
    edit_day = st.number_input(
        "شماره روز:",
        min_value=1,
        max_value=TOTAL_DAYS,
        value=int(st.session_state["edit_day_input"]),
        key="edit_day_input_widget"
    )
    
    st.session_state["edit_day_input"] = edit_day
    
    row_to_edit = df[df["روز"] == edit_day].iloc[0]
    idx_to_edit = df[df["روز"] == edit_day].index[0]
    
    st.info(f"📅 روز {edit_day} — {row_to_edit['سمستر/هفته']} — {row_to_edit['تاریخ']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("① Economic")
        economic = st.number_input(
            "درآمد امروز ($)",
            min_value=0.0,
            value=float(row_to_edit["① Economic"]) if pd.notna(row_to_edit["① Economic"]) else 0.0,
            step=1.0,
            key=f"eco_{edit_day}"
        )
        
        st.subheader("② Control")
        control = st.text_area(
            "تصمیم مستند",
            value="" if is_empty(row_to_edit["② Control"]) else str(row_to_edit["② Control"]),
            height=130,
            key=f"ctrl_{edit_day}"
        )
    
    with col2:
        st.subheader("③ Transferable")
        transferable = st.text_area(
            "دارایی ساخته‌شده",
            value="" if is_empty(row_to_edit["③ Transferable"]) else str(row_to_edit["③ Transferable"]),
            height=130,
            key=f"trans_{edit_day}"
        )
        
        st.subheader("④ Dependence")
        dependence = st.text_area(
            "SOP نوشته‌شده",
            value="" if is_empty(row_to_edit["④ Dependence"]) else str(row_to_edit["④ Dependence"]),
            height=130,
            key=f"dep_{edit_day}"
        )
    
    st.divider()
    note = st.text_input(
        "📝 یادداشت",
        value="" if is_empty(row_to_edit["یادداشت"]) else str(row_to_edit["یادداشت"]),
        key=f"note_{edit_day}"
    )
    
    if st.button("💾 ذخیره", type="primary", use_container_width=True):
        df.loc[idx_to_edit, "① Economic"] = economic
        df.loc[idx_to_edit, "② Control"] = control
        df.loc[idx_to_edit, "③ Transferable"] = transferable
        df.loc[idx_to_edit, "④ Dependence"] = dependence
        df.loc[idx_to_edit, "یادداشت"] = note
        save_log(df)
        st.success(f"✅ روز {edit_day} ذخیره شد!")
        st.balloons()
        st.rerun()

# ============================================================
# صفحه ۲: Log کامل
# ============================================================
elif page == "📋 Log کامل":
    st.title("📋 Log کامل")
    st.caption("جدول ستونی — یا جستجوی عددی")
    
    # ============================================================
    # باکس جستجو
    # ============================================================
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_val = st.text_input(
            "🔍 شماره روز را بنویس:",
            placeholder="مثلاً: 45",
            key="search_box"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 نمایش", type="primary", use_container_width=True, key="btn_search"):
            if search_val.strip():
                try:
                    day_num = int(search_val.strip())
                    if 1 <= day_num <= TOTAL_DAYS:
                        st.session_state["search_result"] = day_num
                        st.rerun()
                    else:
                        st.error(f"عدد باید بین ۱ و {TOTAL_DAYS} باشد")
                except:
                    st.error("لطفاً یک عدد وارد کن")
            else:
                st.warning("عدد را وارد کن")
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("❌ لغو", use_container_width=True, key="btn_cancel"):
            st.session_state["search_result"] = None
            st.rerun()
    
    # ============================================================
    # اگر جستجو نتیجه داد → فقط همان روز
    # ============================================================
    if st.session_state["search_result"] is not None:
        target_day = st.session_state["search_result"]
        result = df[df["روز"] == target_day]
        
        if not result.empty:
            row = result.iloc[0]
            st.divider()
            render_big_day(row, target_day)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ ویرایش این روز", type="primary", 
                            use_container_width=True, key="edit_search_btn"):
                    st.session_state["edit_day_input"] = target_day
                    st.session_state["page"] = "📅 امروز"
                    st.session_state["search_result"] = None
                    st.rerun()
            with col2:
                if st.button("❌ بستن", use_container_width=True, key="close_search_btn"):
                    st.session_state["search_result"] = None
                    st.rerun()
            
            st.stop()
        else:
            st.error(f"روز {target_day} پیدا نشد")
            st.session_state["search_result"] = None
    
    # ============================================================
    # جدول — فقط اگر جستجو نکردی
    # ============================================================
    st.divider()
    
    # فیلترها
    col1, col2, col3 = st.columns(3)
    with col1:
        sem_filter = st.selectbox("سمستر:", ["همه"] + [f"S{i}" for i in range(1, 9)])
    with col2:
        status_filter = st.selectbox("وضعیت:", ["همه", "پر", "خالی"])
    with col3:
        limit = st.number_input("تعداد نمایش:", min_value=10, max_value=640, value=50, step=10)
    
    display_df = df.copy()
    if sem_filter != "همه":
        display_df = display_df[display_df["سمستر/هفته"].str.startswith(sem_filter)]
    
    display_df["_filled"] = display_df.apply(is_day_filled, axis=1)
    
    if status_filter == "پر":
        display_df = display_df[display_df["_filled"]]
    elif status_filter == "خالی":
        display_df = display_df[~display_df["_filled"]]
    
    st.subheader(f"📊 {len(display_df)} روز")
    
    # جدول
    header_cols = st.columns([0.4, 0.8, 0.8, 2.5, 2.5, 2.5, 0.5])
    headers = ["روز", "سمستر", "💰", "🎯 Control", "📦 Transferable", "📋 Dependence", "☐"]
    for col, h in zip(header_cols, headers):
        col.markdown(f"**{h}**")
    
    st.markdown('<hr style="margin: 5px 0;">', unsafe_allow_html=True)
    
    for idx, row in display_df.head(int(limit)).iterrows():
        day_num = int(row["روز"])
        cols = st.columns([0.4, 0.8, 0.8, 2.5, 2.5, 2.5, 0.5])
        
        if is_day_complete(row):
            status_icon = "🟢"
        elif is_day_filled(row):
            status_icon = "🔵"
        else:
            status_icon = "⚪"
        
        cols[0].write(f"**{day_num}**")
        cols[1].write(f"{status_icon} {row['سمستر/هفته']}")
        
        eco_val = row["① Economic"]
        cols[2].write(f"${eco_val:,.0f}" if eco_val > 0 else "—")
        
        ctrl_text = row["② Control"] if not is_empty(row["② Control"]) else "—"
        if len(ctrl_text) > 50:
            ctrl_text = ctrl_text[:50] + "..."
        cols[3].write(ctrl_text)
        
        trans_text = row["③ Transferable"] if not is_empty(row["③ Transferable"]) else "—"
        if len(trans_text) > 50:
            trans_text = trans_text[:50] + "..."
        cols[4].write(trans_text)
        
        dep_text = row["④ Dependence"] if not is_empty(row["④ Dependence"]) else "—"
        if len(dep_text) > 50:
            dep_text = dep_text[:50] + "..."
        cols[5].write(dep_text)
        
        is_expanded = st.session_state.get("expanded_day") == day_num
        
        checkbox = cols[6].checkbox(
            "",
            value=is_expanded,
            key=f"cb_{day_num}",
            label_visibility="collapsed"
        )
        
        if checkbox != is_expanded:
            if checkbox:
                st.session_state["expanded_day"] = day_num
            else:
                st.session_state["expanded_day"] = None
            st.rerun()
        
        st.markdown('<hr style="margin: 3px 0; opacity: 0.2;">', unsafe_allow_html=True)
        
        if st.session_state.get("expanded_day") == day_num:
            render_big_day(row, day_num)
            
            col_edit, col_close = st.columns([1, 1])
            with col_edit:
                if st.button("✏️ ویرایش این روز", key=f"edit_btn_{day_num}", 
                            type="primary", use_container_width=True):
                    st.session_state["edit_day_input"] = day_num
                    st.session_state["page"] = "📅 امروز"
                    st.session_state["expanded_day"] = None
                    st.rerun()
            with col_close:
                if st.button("❌ بستن", key=f"close_btn_{day_num}", 
                            use_container_width=True):
                    st.session_state["expanded_day"] = None
                    st.rerun()
            
            st.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)

# ============================================================
# صفحه ۳: Dashboard
# ============================================================
elif page == "📈 Dashboard":
    st.title("📈 Dashboard")
    
    df["وضعیت"] = df.apply(
        lambda r: "✅" if is_day_complete(r) else ("🔵" if is_day_filled(r) else "⬜"),
        axis=1
    )
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("① Economic", f"${df['① Economic'].sum():,.2f}")
    col2.metric("② Control", f"{len(df[df['② Control'] != ''])}")
    col3.metric("③ Transferable", f"{len(df[df['③ Transferable'] != ''])}")
    col4.metric("④ Dependence", f"{len(df[df['④ Dependence'] != ''])}")
    
    st.divider()
    
    filled = len(df[df["وضعیت"] != "⬜"])
    complete = len(df[df["وضعیت"] == "✅"])
    st.progress(filled / TOTAL_DAYS, text=f"پر: {filled}/{TOTAL_DAYS} | کامل: {complete}/{TOTAL_DAYS}")
    
    st.divider()
    
    st.subheader("📈 درآمد تجمعی")
    df["درآمد تجمعی"] = df["① Economic"].cumsum()
    fig1 = px.line(df, x="روز", y="درآمد تجمعی", title="درآمد تجمعی")
    fig1.update_traces(line_color="#1F4E78", line_width=3)
    st.plotly_chart(fig1, use_container_width=True)
    
    st.subheader("📊 پیشرفت سمسترها")
    sem_data = []
    for s in range(1, 9):
        start_day = (s - 1) * 80 + 1
        end_day = s * 80
        sem_df = df[(df["روز"] >= start_day) & (df["روز"] <= end_day)]
        sem_data.append({
            "سمستر": f"S{s}",
            "کامل": len(sem_df[sem_df["وضعیت"] == "✅"]),
            "پر": len(sem_df[sem_df["وضعیت"] == "🔵"]),
            "خالی": len(sem_df[sem_df["وضعیت"] == "⬜"])
        })
    fig2 = px.bar(
        pd.DataFrame(sem_data), x="سمستر",
        y=["کامل", "پر", "خالی"],
        title="پیشرفت سمسترها",
        barmode="stack",
        color_discrete_map={"کامل": "#C6EFCE", "پر": "#9DC3E6", "خالی": "#FFEB9C"}
    )
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# صفحه ۴: Checkpoint
# ============================================================
elif page == "🎯 Checkpoint":
    st.title("🎯 Checkpoint")
    
    selected_sem = st.selectbox("سمستر:", [f"S{i}" for i in range(1, 9)])
    sem_num = int(selected_sem[1])
    
    start_day = (sem_num - 1) * 80 + 1
    end_day = sem_num * 80
    sem_df = df[(df["روز"] >= start_day) & (df["روز"] <= end_day)]
    
    eco_ok = sem_df["① Economic"].sum() > 0
    ctrl_ok = len(sem_df[sem_df["② Control"] != ""]) > 0
    trans_ok = len(sem_df[sem_df["③ Transferable"] != ""]) > 0
    dep_ok = len(sem_df[sem_df["④ Dependence"] != ""]) > 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("① Economic", f"${sem_df['① Economic'].sum():,.2f}", "✅" if eco_ok else "❌")
    col2.metric("② Control", f"{len(sem_df[sem_df['② Control'] != ''])}", "✅" if ctrl_ok else "❌")
    col3.metric("③ Transferable", f"{len(sem_df[sem_df['③ Transferable'] != ''])}", "✅" if trans_ok else "❌")
    col4.metric("④ Dependence", f"{len(sem_df[sem_df['④ Dependence'] != ''])}", "✅" if dep_ok else "❌")
    
    if eco_ok and ctrl_ok and trans_ok and dep_ok:
        st.success(f"✅ {selected_sem} کامل!")
    else:
        st.warning(f"⚠️ {selected_sem} ناقص")

# ============================================================
# صفحه ۵: راهنما
# ============================================================
elif page == "📖 راهنما":
    st.title("📖 راهنما")
    st.markdown("""
    ## 🕐 قانون
    بعد از هر جلسه → ۳ دقیقه → تمام
    
    ## 📅 امروز
    - شماره روز را انتخاب کن
    - ۴ خانه را پر کن
    - ذخیره
    
    ## 📋 Log کامل
    - جستجوی عددی → عدد بنویس → دکمه «🔍 نمایش»
    - فقط آن روز نشان داده می‌شود
    - دکمه «❌ لغو» → برگشت به جدول
    """)

st.sidebar.divider()
st.sidebar.caption("v3.4")