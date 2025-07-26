import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# โหลดข้อมูล
df = pd.read_excel("cleaned-data.xlsx")

# ค่าทางสถิติภาพรวม
mean_fee = df["ค่าใช้จ่ายต่อเทอม"].mean()
min_fee = df["ค่าใช้จ่ายต่อเทอม"].min()
max_fee = df["ค่าใช้จ่ายต่อเทอม"].max()

# สร้างกราฟภาพรวมล่วงหน้า
overall_df = df.copy()

bar_chart_fig = px.bar(
    overall_df.groupby("มหาวิทยาลัย", as_index=False)["ค่าใช้จ่ายต่อเทอม"].mean(),
    x="มหาวิทยาลัย",
    y="ค่าใช้จ่ายต่อเทอม",
    title="ค่าใช้จ่ายเฉลี่ยต่อมหาวิทยาลัย (ภาพรวมทั้งหมด)",
    color="ค่าใช้จ่ายต่อเทอม",
    width=600,
    height=400
)
bar_chart_fig.update_layout(
    plot_bgcolor='black',
    paper_bgcolor='black',
    font_color='white'
)

pie_chart_fig = px.pie(
    overall_df,
    names="ประเภทหลักสูตร",
    title="สัดส่วนประเภทหลักสูตร (ภาพรวมทั้งหมด)",
    width=600,
    height=400
)
pie_chart_fig.update_layout(
    paper_bgcolor='black',
    font_color='white'
)

# สร้างแอป Dash
app = dash.Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'])

# Layout
app.layout = html.Div([
    html.H1("Dashboard TCAS Computer and Artificial Intelligence Engineering", className="text-3xl font-bold text-center mb-4"),

    # Dropdown เลือกมหาวิทยาลัยอย่างเดียว
    html.Div([
        html.Label("เลือกมหาวิทยาลัย", className="font-bold"),
        dcc.Dropdown(
            id="university-dropdown",
            options=[{"label": u, "value": u} for u in sorted(df["มหาวิทยาลัย"].unique())],
            placeholder="เลือกมหาวิทยาลัย",
            style={"width": "100%", "height": "50px", "fontSize": "16px", "color": "black"}  # Dropdown สีข้อความดำจะอ่านง่ายบน background ขาว dropdown
        ),
    ], className="w-1/3 mx-auto mb-6"),

    # แสดงรายชื่อหลักสูตรและค่าใช้จ่าย
    html.Div(id="fee-display", className="text-xl font-bold text-center mb-6"),

    # สถิติรวม
    html.Div([
        html.Div(f"ค่าใช้จ่ายเฉลี่ย: {mean_fee:,.0f} บาท", className="p-4 rounded-xl", style={"backgroundColor": "#1E40AF", "color": "white"}),
        html.Div(f"ค่าต่ำสุด: {min_fee:,.0f} บาท", className="p-4 rounded-xl", style={"backgroundColor": "#047857", "color": "white"}),
        html.Div(f"ค่าสูงสุด: {max_fee:,.0f} บาท", className="p-4 rounded-xl", style={"backgroundColor": "#B91C1C", "color": "white"}),
    ], className="grid grid-cols-3 gap-4 mb-6"),

    # กราฟภาพรวม (สร้างไว้ล่วงหน้า)
    html.Div([
        dcc.Graph(id="bar-chart", figure=bar_chart_fig, className="rounded-xl shadow", style={"width": "600px", "height": "400px"}),
        dcc.Graph(id="pie-chart", figure=pie_chart_fig, className="rounded-xl shadow", style={"width": "600px", "height": "400px"}),
    ], className="grid grid-cols-2 gap-6 mb-6 mx-auto"),

    # ตารางข้อมูลทั้งหมด
    dash_table.DataTable(
        id="table",
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict("records"),
        style_table={'overflowX': 'auto', 'backgroundColor': 'black'},
        style_header={'backgroundColor': '#222', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'backgroundColor': '#111', 'color': 'white', 'padding': '5px', 'textAlign': 'left'}
    )
], className="p-6 min-h-screen", style={"backgroundColor": "black", "color": "white"})


# Callback แสดงรายชื่อหลักสูตรและค่าใช้จ่าย ตามมหาวิทยาลัยที่เลือก
@app.callback(
    Output("fee-display", "children"),
    Input("university-dropdown", "value")
)
def update_fee(university):
    if not university:
        return ""

    filtered = df[df["มหาวิทยาลัย"] == university]

    if filtered.empty:
        return "ไม่พบข้อมูลที่เลือก"

    lines = [f"{row['ชื่อหลักสูตร']} : {row['ค่าใช้จ่ายต่อเทอม']:,.0f} บาท" for _, row in filtered.iterrows()]

    return html.Div([
        html.Div(f"พบ {len(filtered)} หลักสูตรในมหาวิทยาลัย {university}:"),
        html.Ul([html.Li(line) for line in lines], style={"textAlign": "left", "margin": "auto", "maxWidth": "600px"})
    ], style={"color": "white"})


if __name__ == "__main__":
    app.run(debug=True, port=8050)
