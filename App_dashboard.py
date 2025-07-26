import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# โหลดข้อมูล
df = pd.read_excel("cleaned-data.xlsx")

# สร้างแอป Dash
app = dash.Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'])

# ค่าทางสถิติ
mean_fee = df["ค่าใช้จ่ายต่อเทอม"].mean()
min_fee = df["ค่าใช้จ่ายต่อเทอม"].min()
max_fee = df["ค่าใช้จ่ายต่อเทอม"].max()

# Layout
app.layout = html.Div([
    html.H1("Dashboard หลักสูตรและค่าใช้จ่าย", className="text-3xl font-bold text-center mb-4"),

    # ส่วน Filter
    html.Div([
        html.Div([
            html.Label("เลือกมหาวิทยาลัย", className="font-bold"),
            dcc.Dropdown(
                id="university-dropdown",
                options=[{"label": u, "value": u} for u in sorted(df["มหาวิทยาลัย"].unique())],
                placeholder="เลือกมหาวิทยาลัย",
                style={"width": "100%", "height": "50px", "fontSize": "16px"}
            ),
        ], className="w-full"),

        html.Div([
            html.Label("เลือกชื่อหลักสูตร", className="font-bold"),
            dcc.Dropdown(
                id="program-dropdown",
                placeholder="เลือกชื่อหลักสูตร",
                style={"width": "100%", "height": "50px", "fontSize": "16px"}
            ),
        ], className="w-full"),

        html.Div([
            html.Label("เลือกประเภทหลักสูตร", className="font-bold"),
            dcc.Dropdown(
                id="type-dropdown",
                placeholder="เลือกประเภทหลักสูตร",
                style={"width": "100%", "height": "50px", "fontSize": "16px"}
            ),
        ], className="w-full"),

        html.Div([
            html.Label("เลือกวิทยาเขต", className="font-bold"),
            dcc.Dropdown(
                id="campus-dropdown",
                placeholder="เลือกวิทยาเขต",
                style={"width": "100%", "height": "50px", "fontSize": "16px"}
            ),
        ], className="w-full"),
    ], className="grid grid-cols-4 gap-4 mb-6"),

    # แสดงค่าเทอม
    html.Div(id="fee-display", className="text-xl font-bold text-center mb-6"),

    # สถิติรวม
    html.Div([
        html.Div(f"ค่าใช้จ่ายเฉลี่ย: {mean_fee:,.0f} บาท", className="p-4 bg-blue-100 rounded-xl"),
        html.Div(f"ค่าต่ำสุด: {min_fee:,.0f} บาท", className="p-4 bg-green-100 rounded-xl"),
        html.Div(f"ค่าสูงสุด: {max_fee:,.0f} บาท", className="p-4 bg-red-100 rounded-xl")
    ], className="grid grid-cols-3 gap-4 mb-6"),

    # กราฟ
    html.Div([
        dcc.Graph(id="bar-chart", className="rounded-xl shadow"),
        dcc.Graph(id="pie-chart", className="rounded-xl shadow"),
    ], className="grid grid-cols-2 gap-6 mb-6"),

    # ตารางข้อมูล
    dash_table.DataTable(
        id="table",
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict("records"),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'lightblue', 'fontWeight': 'bold'},
        style_cell={'padding': '5px', 'textAlign': 'left'}
    )
], className="p-6 bg-gray-50 min-h-screen")


# --- Callback สำหรับอัปเดตตัวเลือกใน Dropdown อื่นๆ ---
@app.callback(
    [Output("program-dropdown", "options"),
     Output("type-dropdown", "options"),
     Output("campus-dropdown", "options")],
    Input("university-dropdown", "value")
)
def update_dropdowns(university):
    if university:
        filtered = df[df["มหาวิทยาลัย"] == university]
        program_opts = [{"label": p, "value": p} for p in sorted(filtered["ชื่อหลักสูตร"].unique())]
        type_opts = [{"label": t, "value": t} for t in sorted(filtered["ประเภทหลักสูตร"].unique())]
        campus_opts = [{"label": c, "value": c} for c in sorted(filtered["วิทยาเขต"].unique())]
        return program_opts, type_opts, campus_opts
    else:
        return [], [], []


# --- Callback แสดงค่าเทอม ---
@app.callback(
    Output("fee-display", "children"),
    [Input("university-dropdown", "value"),
     Input("program-dropdown", "value"),
     Input("type-dropdown", "value"),
     Input("campus-dropdown", "value")]
)
def update_fee(university, program, course_type, campus):
    filtered = df.copy()
    if university:
        filtered = filtered[filtered["มหาวิทยาลัย"] == university]
    if program:
        filtered = filtered[filtered["ชื่อหลักสูตร"] == program]
    if course_type:
        filtered = filtered[filtered["ประเภทหลักสูตร"] == course_type]
    if campus:
        filtered = filtered[filtered["วิทยาเขต"] == campus]

    if len(filtered) == 1:
        return f"ค่าใช้จ่ายต่อเทอม: {filtered['ค่าใช้จ่ายต่อเทอม'].values[0]:,.0f} บาท"
    elif len(filtered) > 1:
        # สร้างข้อความรายชื่อหลักสูตร + ค่าใช้จ่ายต่อเทอมแต่ละรายการ
        lines = []
        for _, row in filtered.iterrows():
            lines.append(f"{row['ชื่อหลักสูตร']} : {row['ค่าใช้จ่ายต่อเทอม']:,.0f} บาท")
        return html.Div([
            html.Div("พบข้อมูลหลายรายการ:"),
            html.Ul([html.Li(line) for line in lines], style={"textAlign": "left", "margin": "auto", "maxWidth": "600px"})
        ])
    else:
        return "ไม่พบข้อมูลที่เลือก"

# --- Callback อัปเดตกราฟ ---
@app.callback(
    [Output("bar-chart", "figure"),
     Output("pie-chart", "figure")],
    [Input("university-dropdown", "value"),
     Input("type-dropdown", "value")]
)
def update_graphs(university, course_type):
    # ใช้ข้อมูลภาพรวมทั้งหมดโดยไม่กรอง
    overall_df = df.copy()

    # กราฟแท่ง: ค่าใช้จ่ายเฉลี่ยต่อมหาวิทยาลัยภาพรวมทั้งหมด
    bar_chart = px.bar(
        overall_df.groupby("มหาวิทยาลัย", as_index=False)["ค่าใช้จ่ายต่อเทอม"].mean(),
        x="มหาวิทยาลัย",
        y="ค่าใช้จ่ายต่อเทอม",
        title="ค่าใช้จ่ายเฉลี่ยต่อมหาวิทยาลัย (ภาพรวมทั้งหมด)",
        color="ค่าใช้จ่ายต่อเทอม",
        width=600,
        height=400
    )

    # กราฟวงกลม: สัดส่วนประเภทหลักสูตรภาพรวมทั้งหมด
    pie_chart = px.pie(
        overall_df,
        names="ประเภทหลักสูตร",
        title="สัดส่วนประเภทหลักสูตร (ภาพรวมทั้งหมด)",
        width=600,
        height=400
    )

    return bar_chart, pie_chart

if __name__ == "__main__":
    app.run(debug=True, port=8050)
