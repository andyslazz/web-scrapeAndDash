import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# โหลดข้อมูลจาก Excel
df = pd.read_excel("programs_ai.xlsx")

# เตรียมคอลัมน์ให้แสดง
columns_to_display = [col for col in df.columns if col != "ลิงก์"]

# สร้าง Dash App
app = dash.Dash(__name__)
app.title = "AI Engineering Programs Dashboard"

# Layout
app.layout = html.Div([
    html.H1("📊 AI Engineering Programs in Thai Universities", style={'textAlign': 'center'}),

    dcc.Dropdown(
        id='university-dropdown',
        options=[{'label': uni, 'value': uni} for uni in sorted(df['มหาวิทยาลัย'].unique())],
        placeholder="เลือกมหาวิทยาลัย",
        style={'width': '50%', 'margin': '0 auto'}
    ),

    html.Div(id='program-info', style={'padding': '20px 40px'})
])

# Callback: เปลี่ยนข้อมูลตามมหาวิทยาลัยที่เลือก
@app.callback(
    Output('program-info', 'children'),
    [Input('university-dropdown', 'value')]
)
def update_output(selected_uni):
    if not selected_uni:
        return html.Div("กรุณาเลือกมหาวิทยาลัยเพื่อแสดงข้อมูล", style={"fontSize": 18})

    filtered = df[df['มหาวิทยาลัย'] == selected_uni]

    children = []
    for idx, row in filtered.iterrows():
        block = html.Div([
            html.H3(f"🏫 {row.get('คณะ', 'ไม่ระบุ')} - {row.get('สาขาวิชา', '')}"),
            html.Ul([html.Li(f"{col}: {row[col]}") for col in columns_to_display if col not in ['มหาวิทยาลัย', 'คณะ', 'สาขาวิชา']]),
            html.A("🔗 เปิดลิงก์", href=row["ลิงก์"], target="_blank")
        ], style={
            "border": "1px solid #ccc",
            "borderRadius": "10px",
            "padding": "15px",
            "marginBottom": "20px",
            "backgroundColor": "#f9f9f9"
        })

        children.append(block)

    return children

# รันแอป
if __name__ == '__main__':
    app.run(debug=True)
