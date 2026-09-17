"""
Ownership Log Generator — v3.4
یک اسکریپت، کل فایل Ownership Log را می‌سازد
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, BarChart, Reference
from datetime import datetime, timedelta
import os

# ============================================================
# تنظیمات
# ============================================================
FILE_NAME = "ownership_log.xlsx"
TOTAL_DAYS = 640  # یا 320 اگر 20/80
START_DATE = datetime.now().date()

# ============================================================
# استایل‌ها
# ============================================================
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=12)
SUBHEADER_FILL = PatternFill("solid", fgColor="D9E1F2")
SUBHEADER_FONT = Font(bold=True, color="1F4E78")
TITLE_FONT = Font(bold=True, size=16, color="1F4E78")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center")
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)
STATUS_OK = PatternFill("solid", fgColor="C6EFCE")
STATUS_NO = PatternFill("solid", fgColor="FFEB9C")

# ============================================================
# تابع کمکی: سمستر و هفته از روز
# ============================================================
def get_semester_week(day):
    """روز ۱ تا ۶۴۰ → سمستر و هفته"""
    semester = (day - 1) // 80 + 1
    week_in_sem = ((day - 1) % 80) // 5 + 1
    return f"S{semester}/W{week_in_sem}"

# ============================================================
# ساخت Workbook
# ============================================================
wb = openpyxl.Workbook()

# ------------------------------------------------------------
# Sheet 1: Daily Log
# ------------------------------------------------------------
ws = wb.active
ws.title = "Daily Log"

# عنوان
ws.merge_cells("A1:J1")
ws["A1"] = "📊 OWNERSHIP LOG — v3.4"
ws["A1"].font = TITLE_FONT
ws["A1"].alignment = CENTER

ws.merge_cells("A2:J2")
ws["A2"] = "ثبت روزانه · هر روز یک بلوک · بعد از جلسه · بدون دروغ · بدون Skip"
ws["A2"].alignment = CENTER

# هدرها
headers = [
    "#", "تاریخ", "سمستر/هفته", "روز",
    "① Economic ($)", "② Control (تصمیم)",
    "③ Transferable (دارایی)", "④ Dependence (SOP)",
    "وضعیت", "یادداشت"
]
for col, header in enumerate(headers, start=1):
    cell = ws.cell(row=4, column=col, value=header)
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = CENTER
    cell.border = THIN_BORDER

# داده‌ها
for day in range(1, TOTAL_DAYS + 1):
    row = day + 4
    sem_week = get_semester_week(day)
    date = START_DATE + timedelta(days=day - 1)
    
    ws.cell(row=row, column=1, value=day).alignment = CENTER
    ws.cell(row=row, column=2, value=date.strftime("%Y-%m-%d")).alignment = CENTER
    ws.cell(row=row, column=3, value=sem_week).alignment = CENTER
    ws.cell(row=row, column=4, value=f"روز {day}").alignment = CENTER
    
    # فرمول وضعیت
    status_cell = ws.cell(
        row=row, column=9,
        value=f'=IF(AND(E{row}<>"",F{row}<>"",G{row}<>"",H{row}<>""),"✅","⬜")'
    )
    status_cell.alignment = CENTER
    status_cell.border = THIN_BORDER
    
    # حاشیه‌ها
    for col in range(1, 11):
        ws.cell(row=row, column=col).border = THIN_BORDER

# عرض ستون‌ها
widths = [5, 12, 12, 8, 15, 25, 25, 25, 10, 20]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w

ws.freeze_panes = "A5"

# ------------------------------------------------------------
# Sheet 2: Dashboard
# ------------------------------------------------------------
dash = wb.create_sheet("Dashboard")

dash.merge_cells("A1:F1")
dash["A1"] = "📈 OWNERSHIP DASHBOARD"
dash["A1"].font = TITLE_FONT
dash["A1"].alignment = CENTER

dash.merge_cells("A2:F2")
dash["A2"] = "مرور تجمعی · آپدیت خودکار"
dash["A2"].alignment = CENTER

# ۴ بُعد
dims = [
    ("① Economic — مجموع درآمد", f"=SUM('Daily Log'!E5:E{4+TOTAL_DAYS})", "$"),
    ("② Control — تعداد تصمیم", f"=COUNTA('Daily Log'!F5:F{4+TOTAL_DAYS})", "تصمیم"),
    ("③ Transferable — تعداد دارایی", f"=COUNTA('Daily Log'!G5:G{4+TOTAL_DAYS})", "دارایی"),
    ("④ Dependence — تعداد SOP", f"=COUNTA('Daily Log'!H5:H{4+TOTAL_DAYS})", "SOP"),
]

dash["A4"] = "📊 وضعیت تجمعی"
dash["A4"].font = SUBHEADER_FONT

for i, (label, formula, unit) in enumerate(dims):
    r = 5 + i
    dash.cell(row=r, column=1, value=label).font = Font(bold=True)
    dash.cell(row=r, column=2, value=formula)
    dash.cell(row=r, column=3, value=unit)

# پیشرفت
dash["A10"] = "📅 پیشرفت"
dash["A10"].font = SUBHEADER_FONT
dash["A11"] = "روزهای تکمیل‌شده"
dash["B11"] = f'=COUNTIF(\'Daily Log\'!I5:I{4+TOTAL_DAYS},"✅")'
dash["A12"] = "درصد پیشرفت"
dash["B12"] = f'=COUNTIF(\'Daily Log\'!I5:I{4+TOTAL_DAYS},"✅")/{TOTAL_DAYS}'
dash["B12"].number_format = "0.0%"

# Checkpoint هفتگی (خلاصه — 8 سمستر)
dash["A15"] = "📋 CHECKPOINT سمسترها"
dash["A15"].font = SUBHEADER_FONT

dash["A16"] = "سمستر"
dash["B16"] = "روزهای ✅"
dash["C16"] = "درصد"
for col in ["A16", "B16", "C16"]:
    dash[col].fill = HEADER_FILL
    dash[col].font = HEADER_FONT
    dash[col].alignment = CENTER

for s in range(1, 9):
    r = 16 + s
    start_day = (s - 1) * 80 + 1
    end_day = s * 80
    start_row = start_day + 4
    end_row = end_day + 4
    
    dash.cell(row=r, column=1, value=f"S{s}")
    dash.cell(row=r, column=2, 
              value=f'=COUNTIF(\'Daily Log\'!I{start_row}:I{end_row},"✅")')
    dash.cell(row=r, column=3,
              value=f'=COUNTIF(\'Daily Log\'!I{start_row}:I{end_row},"✅")/80')
    dash.cell(row=r, column=3).number_format = "0.0%"

dash.column_dimensions["A"].width = 35
dash.column_dimensions["B"].width = 20
dash.column_dimensions["C"].width = 15
dash.column_dimensions["D"].width = 15
dash.column_dimensions["E"].width = 15
dash.column_dimensions["F"].width = 15

# ------------------------------------------------------------
# Sheet 3: Semester Check
# ------------------------------------------------------------
sem = wb.create_sheet("Semester Check")

sem.merge_cells("A1:E1")
sem["A1"] = "🎯 SEMESTER CHECKPOINT"
sem["A1"].font = TITLE_FONT
sem["A1"].alignment = CENTER

sem.merge_cells("A2:E2")
sem["A2"] = "پایان هر سمستر · ۳۰ دقیقه مرور · ۴ بُعد Ownership"
sem["A2"].alignment = CENTER

semester_goals = {
    1: "$1",
    2: "$100",
    3: "اولین محصول",
    4: "Distribution",
    5: "Unit Economics",
    6: "Automation",
    7: "Scale",
    8: "Ownership کامل",
}

row = 4
for s in range(1, 9):
    sem.merge_cells(f"A{row}:E{row}")
    sem[f"A{row}"] = f"📊 سمستر {s} — هدف: {semester_goals[s]}"
    sem[f"A{row}"].font = SUBHEADER_FONT
    sem[f"A{row}"].fill = SUBHEADER_FILL
    row += 1
    
    headers_sem = ["بُعد", "سؤال ارزیابی", "نتیجه", "✅/❌"]
    for col, h in enumerate(headers_sem, start=1):
        c = sem.cell(row=row, column=col, value=h)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = CENTER
    row += 1
    
    dimensions = [
        ("① Economic", "درآمد واقعی دریافت کردم؟"),
        ("② Control", "تصمیم مستند دارم؟"),
        ("③ Transferable", "دارایی قابل انتقال دارم؟"),
        ("④ Dependence", "SOP نوشتم؟"),
    ]
    for dim, q in dimensions:
        sem.cell(row=row, column=1, value=dim)
        sem.cell(row=row, column=2, value=q)
        sem.cell(row=row, column=4, 
                 value=f'=IF(C{row}<>"","✅","⬜")').alignment = CENTER
        row += 1
    
    sem.cell(row=row, column=1, value="تصمیم نهایی:")
    sem.cell(row=row, column=2, 
             value="Continue / Modify / Kill / Pivot")
    row += 2

sem.column_dimensions["A"].width = 20
sem.column_dimensions["B"].width = 40
sem.column_dimensions["C"].width = 30
sem.column_dimensions["D"].width = 10
sem.column_dimensions["E"].width = 20

# ------------------------------------------------------------
# Sheet 4: راهنما
# ------------------------------------------------------------
guide = wb.create_sheet("راهنما")
guide.column_dimensions["A"].width = 80

guide_text = [
    ("📖 راهنمای استفاده", TITLE_FONT),
    ("", None),
    ("🕐 قانون اصلی: بعد از هر جلسه (۹۰ دقیقه) → ۳ دقیقه Log پر کن → تمام", None),
    ("", None),
    ("📅 Daily Log:", SUBHEADER_FONT),
    ("   ردیف امروز را پیدا کن → ۴ خانه پر کن", None),
    ("   ① ستون E: Economic — چه چیزی به دست آوردم؟ (اگر صفر → بنویس 0)", None),
    ("   ② ستون F: Control — چه تصمیمی گرفتم؟", None),
    ("   ③ ستون G: Transferable — چه دارایی ساختم؟", None),
    ("   ④ ستون H: Dependence — چه SOP نوشتم؟", None),
    ("   ⚡ ستون I: وضعیت — خودکار آپدیت می‌شود", None),
    ("", None),
    ("📊 Dashboard:", SUBHEADER_FONT),
    ("   آمار تجمعی به‌صورت خودکار نشان می‌دهد", None),
    ("", None),
    ("🎯 Semester Check:", SUBHEADER_FONT),
    ("   پایان هر سمستر → ۴ بُعد را چک کن", None),
    ("   اگر هر ۴ ✅ → سمستر بعد", None),
    ("   اگر بعضی ❌ → همان سمستر را دوباره اجرا کن", None),
    ("", None),
    ("⚠️ سه قانون مهم:", SUBHEADER_FONT),
    ("   ① دروغ نگو — 0 را بنویس، نه 100 که نداشتی", None),
    ("   ② صفر را بنویس — خانه خالی = غلط، 0 = درست", None),
    ("   ③ بلوک قدیمی را پاک نکن — Log = تاریخچه‌ی رشد تو", None),
    ("", None),
    ("💡 اگر یک روز فراموش کردی:", SUBHEADER_FONT),
    ("   فردا دو ردیف پر کن (روز فراموش‌شده + امروز)", None),
]

for i, (text, font) in enumerate(guide_text, start=1):
    c = guide.cell(row=i, column=1, value=text)
    if font:
        c.font = font

# ============================================================
# ذخیره
# ============================================================
wb.save(FILE_NAME)
print(f"✅ فایل ساخته شد: {FILE_NAME}")
print(f"📊 تعداد روزها: {TOTAL_DAYS}")
print(f"📅 تاریخ شروع: {START_DATE}")
print(f"📅 تاریخ پایان: {START_DATE + timedelta(days=TOTAL_DAYS - 1)}")
print(f"\n🚀 حالا فایل را باز کن و شروع کن.")