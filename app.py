import dash
from dash import dcc, html, ctx
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# 1. Initialize the Master Web App
# suppress_callback_exceptions=True is REQUIRED for multi-page apps
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Universal Kinematics Dashboard"

# 2. The Main URL Router Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# =====================================================================
# 3. PAGE LAYOUTS
# =====================================================================

def layout_home():
    return html.Div(style={'textAlign': 'center', 'padding': '100px', 'fontFamily': 'Arial'}, children=[
        html.H1("⚙️ Universal Kinematics Dashboard"),
        html.P("Select a mechanism to simulate:", style={'fontSize': '20px'}),
        html.Br(),
        dcc.Link(html.Button("Four-Bar Mechanism", style={'padding': '20px', 'fontSize': '20px', 'margin': '10px', 'cursor': 'pointer', 'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none', 'borderRadius': '10px'}), href='/fourbar'),
        dcc.Link(html.Button("Slider-Crank Mechanism", style={'padding': '20px', 'fontSize': '20px', 'margin': '10px', 'cursor': 'pointer', 'backgroundColor': '#28A745', 'color': 'white', 'border': 'none', 'borderRadius': '10px'}), href='/slidercrank')
    ])

def layout_4bar():
    return html.Div(style={'fontFamily': 'Arial', 'display': 'flex', 'flexDirection': 'row'}, children=[
        html.Div(style={'width': '30%', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'height': '100vh', 'overflowY': 'auto'}, children=[
            dcc.Link("⬅️ Back to Main Menu", href='/', style={'fontSize': '16px', 'textDecoration': 'none', 'color': 'blue', 'fontWeight': 'bold'}),
            html.H2("Four-Bar Controls"),
            html.H4(id='status-text-4b', style={'color': 'green'}),
            html.Label("L1 (Ground)"), dcc.Slider(id='sl-L1-4b', min=1, max=20, step=0.5, value=8),
            html.Label("L2 (Crank)"), dcc.Slider(id='sl-L2-4b', min=1, max=20, step=0.5, value=3),
            html.Label("L3 (Coupler)"), dcc.Slider(id='sl-L3-4b', min=1, max=20, step=0.5, value=7),
            html.Label("L4 (Rocker)"), dcc.Slider(id='sl-L4-4b', min=1, max=20, step=0.5, value=6),
            html.Hr(),
            html.Label("Coupler Length"), dcc.Slider(id='sl-CpL-4b', min=0, max=15, step=0.5, value=4),
            html.Label("Coupler Angle (deg)"), dcc.Slider(id='sl-CpA-4b', min=-180, max=180, step=5, value=45),
            html.Hr(),
            html.Label("Speed"), dcc.Slider(id='sl-speed-4b', min=1, max=10, step=1, value=3),
            html.Hr(),
            html.Button("📊 Generate Plots", id="btn-plots-4b", n_clicks=0, style={'width': '100%', 'padding': '10px', 'marginBottom': '10px'}),
            html.Button("💾 Download CSV", id="btn-download-4b", n_clicks=0, style={'width': '100%', 'padding': '10px', 'backgroundColor': '#4CAF50', 'color': 'white'}),
            dcc.Download(id="download-csv-4b"),
            dcc.Interval(id='anim-loop-4b', interval=150, n_intervals=0)
        ]),
        html.Div(style={'width': '70%', 'padding': '0px', 'display': 'flex', 'flexDirection': 'column', 'height': '100vh'}, children=[
            html.Div(style={'height': '60%'}, children=[dcc.Graph(id='live-graph-4b', style={'height': '100%'})]),
            html.Div(id='static-plots-4b', style={'height': '40%', 'display': 'flex', 'flexDirection': 'row', 'backgroundColor': '#f1f1f1'})
        ])
    ])

def layout_slider():
    return html.Div(style={'fontFamily': 'Arial', 'display': 'flex', 'flexDirection': 'row'}, children=[
        html.Div(style={'width': '30%', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'height': '100vh', 'overflowY': 'auto'}, children=[
            dcc.Link("⬅️ Back to Main Menu", href='/', style={'fontSize': '16px', 'textDecoration': 'none', 'color': 'blue', 'fontWeight': 'bold'}),
            html.H2("Slider-Crank Controls"),
            html.H4(id='status-text-sc', style={'color': 'green'}),
            html.Label("Crank Radius (r)"), dcc.Slider(id='sl-R-sc', min=1, max=15, step=0.5, value=3),
            html.Label("Connecting Rod (L)"), dcc.Slider(id='sl-L-sc', min=1, max=30, step=0.5, value=10),
            html.Label("Track Offset (e)"), dcc.Slider(id='sl-E-sc', min=-10, max=10, step=0.5, value=0),
            html.Hr(),
            html.Label("Speed"), dcc.Slider(id='sl-speed-sc', min=1, max=10, step=1, value=3),
            html.Hr(),
            html.Button("📊 Generate Plots", id="btn-plots-sc", n_clicks=0, style={'width': '100%', 'padding': '10px', 'marginBottom': '10px'}),
            html.Button("💾 Download CSV", id="btn-download-sc", n_clicks=0, style={'width': '100%', 'padding': '10px', 'backgroundColor': '#4CAF50', 'color': 'white'}),
            dcc.Download(id="download-csv-sc"),
            dcc.Interval(id='anim-loop-sc', interval=150, n_intervals=0)
        ]),
        html.Div(style={'width': '70%', 'padding': '0px', 'display': 'flex', 'flexDirection': 'column', 'height': '100vh'}, children=[
            html.Div(style={'height': '60%'}, children=[dcc.Graph(id='live-graph-sc', style={'height': '100%'})]),
            html.Div(id='static-plots-sc', style={'height': '40%', 'display': 'flex', 'flexDirection': 'row', 'backgroundColor': '#f1f1f1'})
        ])
    ])

# =====================================================================
# 4. ROUTER CALLBACK (Switches pages)
# =====================================================================
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/fourbar':
        return layout_4bar()
    elif pathname == '/slidercrank':
        return layout_slider()
    else:
        return layout_home()

# =====================================================================
# 5. FOUR-BAR CALLBACKS
# =====================================================================
@app.callback(
    [Output('live-graph-4b', 'figure'), Output('status-text-4b', 'children'), Output('status-text-4b', 'style')],
    [Input('sl-L1-4b', 'value'), Input('sl-L2-4b', 'value'), Input('sl-L3-4b', 'value'), Input('sl-L4-4b', 'value'), Input('sl-CpL-4b', 'value'), Input('sl-CpA-4b', 'value'), Input('sl-speed-4b', 'value'), Input('anim-loop-4b', 'n_intervals')]
)
def update_4b_anim(L1, L2, L3, L4, CpL, CpA_deg, speed, n_intervals):
    min_other = min(L1, L3, L4)
    if L2 > min_other - 0.5: L2 = max(1.0, min_other - 0.5)
    CpA = np.deg2rad(CpA_deg)
    is_grashof = sorted([L1, L2, L3, L4])[0] + sorted([L1, L2, L3, L4])[3] < sorted([L1, L2, L3, L4])[1] + sorted([L1, L2, L3, L4])[2]
    status = "Status: Grashof" if is_grashof else "Status: Non-Grashof"
    
    th2_sw = np.linspace(0, 2*np.pi, 360)
    xA_sw, yA_sw = L2 * np.cos(th2_sw), L2 * np.sin(th2_sw)
    dist_sw = np.sqrt((L1 - xA_sw)**2 + (-yA_sw)**2)
    valid = (dist_sw <= (L3 + L4)) & (dist_sw >= abs(L3 - L4))
    
    fig = go.Figure()
    if not np.any(valid): return fig, "Cannot Assemble", {'color': 'red'}

    th2_v = th2_sw[valid]
    xA_v, yA_v, d_v = xA_sw[valid], yA_sw[valid], dist_sw[valid]
    th3_v = np.arctan2(-yA_v, L1 - xA_v) - np.arccos((L3**2 + d_v**2 - L4**2) / (2 * L3 * d_v))
    xP_v, yP_v = xA_v + CpL * np.cos(th3_v + CpA), yA_v + CpL * np.sin(th3_v + CpA)
    fig.add_trace(go.Scatter(x=xP_v, y=yP_v, mode='lines', line=dict(color='cyan', dash='dash')))

    num_frames = len(th2_v)
    step_idx = n_intervals * speed * 4
    if is_grashof: idx = int(step_idx % num_frames)
    else:
        idx = int(step_idx % (2 * num_frames))
        if idx >= num_frames: idx = 2 * num_frames - idx - 1
            
    th2_cur = th2_v[idx]
    xA, yA = L2 * np.cos(th2_cur), L2 * np.sin(th2_cur)
    dist = np.sqrt((L1 - xA)**2 + (-yA)**2)
    th3 = np.arctan2(-yA, L1 - xA) - np.arccos((L3**2 + dist**2 - L4**2) / (2 * L3 * dist))
    xB, yB = xA + L3 * np.cos(th3), yA + L3 * np.sin(th3)
    xP, yP = xA + CpL * np.cos(th3 + CpA), yA + CpL * np.sin(th3 + CpA)

    fig.add_trace(go.Scatter(x=[0, L1], y=[0, 0], mode='lines+markers', line=dict(color='black', width=5), marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=[0, xA], y=[0, yA], mode='lines+markers', line=dict(color='red', width=5), marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=[xA, xB], y=[yA, yB], mode='lines+markers', line=dict(color='green', width=5), marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=[L1, xB], y=[0, yB], mode='lines+markers', line=dict(color='blue', width=5), marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=[xA, xB, xP, xA], y=[yA, yB, yP, yA], fill='toself', fillcolor='rgba(0, 255, 255, 0.4)', line=dict(color='rgba(255,255,255,0)')))

    max_reach = max([L1, L2, L3, L4]) * 2.5
    fig.update_layout(xaxis=dict(range=[-max_reach/2, L1 + max_reach/2]), yaxis=dict(range=[-max_reach/2, max_reach/2], scaleanchor="x", scaleratio=1), showlegend=False, uirevision='c', margin=dict(l=20, r=20, t=20, b=20))
    return fig, status, {'color': 'green'} if is_grashof else {'color': 'red'}

@app.callback(
    [Output('static-plots-4b', 'children'), Output('download-csv-4b', 'data')],
    [Input('btn-plots-4b', 'n_clicks'), Input('btn-download-4b', 'n_clicks')],
    [State('sl-L1-4b', 'value'), State('sl-L2-4b', 'value'), State('sl-L3-4b', 'value'), State('sl-L4-4b', 'value')]
)
def update_4b_data(btn_p, btn_d, L1, L2, L3, L4):
    if not ctx.triggered: return dash.no_update, dash.no_update
    trig = ctx.triggered[0]['prop_id']
    
    th2_sw = np.linspace(0, 2*np.pi, 360)
    xA_sw, yA_sw = L2 * np.cos(th2_sw), L2 * np.sin(th2_sw)
    dist_sw = np.sqrt((L1 - xA_sw)**2 + (-yA_sw)**2)
    valid = (dist_sw <= (L3 + L4)) & (dist_sw >= abs(L3 - L4))
    if not np.any(valid): return dash.no_update, dash.no_update

    th2_v = th2_sw[valid]
    xA_v, yA_v, d_v = xA_sw[valid], yA_sw[valid], dist_sw[valid]
    th3_v = np.arctan2(-yA_v, L1 - xA_v) - np.arccos((L3**2 + d_v**2 - L4**2) / (2 * L3 * d_v))
    xB_v, yB_v = xA_v + L3 * np.cos(th3_v), yA_v + L3 * np.sin(th3_v)
    th4_v = np.arctan2(yB_v, xB_v - L1)
    
    om4 = np.gradient(np.unwrap(th4_v)) / np.gradient(th2_v)
    al4 = np.gradient(om4) / np.gradient(th2_v)

    if 'btn-plots-4b' in trig:
        f_v = go.Figure(data=go.Scatter(x=np.rad2deg(th2_v), y=om4, line=dict(color='blue'))); f_v.update_layout(title="Velocity (ω4)", margin=dict(l=20, r=20, t=40, b=20))
        f_a = go.Figure(data=go.Scatter(x=np.rad2deg(th2_v), y=al4, line=dict(color='red'))); f_a.update_layout(title="Accel (α4)", margin=dict(l=20, r=20, t=40, b=20))
        return [dcc.Graph(figure=f_v, style={'width': '50%'}), dcc.Graph(figure=f_a, style={'width': '50%'})], dash.no_update
    elif 'btn-download-4b' in trig:
        df = pd.DataFrame({'Crank_Angle': np.rad2deg(th2_v), 'Velocity_w4': om4, 'Acceleration_a4': al4})
        return dash.no_update, dcc.send_data_frame(df.to_csv, "fourbar_data.csv", index=False)

# =====================================================================
# 6. SLIDER-CRANK CALLBACKS
# =====================================================================
@app.callback(
    [Output('live-graph-sc', 'figure'), Output('status-text-sc', 'children'), Output('status-text-sc', 'style')],
    [Input('sl-R-sc', 'value'), Input('sl-L-sc', 'value'), Input('sl-E-sc', 'value'), Input('sl-speed-sc', 'value'), Input('anim-loop-sc', 'n_intervals')]
)
def update_sc_anim(r, L, e, speed, n_intervals):
    if L < r + abs(e): L = r + abs(e) + 0.5
    th2_sw = np.linspace(0, 2*np.pi, 360)
    yA_sw = r * np.sin(th2_sw)
    valid = L >= np.abs(e - yA_sw)
    
    fig = go.Figure()
    if not np.any(valid): return fig, "Cannot Assemble", {'color': 'red'}

    th2_v = th2_sw[valid]
    idx = int((n_intervals * speed * 4) % len(th2_v))
            
    th2_cur = th2_v[idx]
    xA, yA = r * np.cos(th2_cur), r * np.sin(th2_cur)
    th3 = np.arcsin((e - yA) / L)
    xB, yB = xA + L * np.cos(th3), e

    fig.add_trace(go.Scatter(x=[-(r+L+5), r+L+5], y=[e, e], mode='lines', line=dict(color='black', dash='dash')))
    fig.add_trace(go.Scatter(x=[0, xA], y=[0, yA], mode='lines+markers', line=dict(color='red', width=5), marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=[xA, xB], y=[yA, yB], mode='lines+markers', line=dict(color='green', width=5), marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=[xB-1.5, xB+1.5, xB+1.5, xB-1.5, xB-1.5], y=[yB-1, yB-1, yB+1, yB+1, yB-1], fill='toself', fillcolor='rgba(0, 0, 255, 0.4)', line=dict(color='blue')))

    fig.update_layout(xaxis=dict(range=[-(r+L+2), r+L+5]), yaxis=dict(range=[min(-r, e-2)-4, max(r, e+2)+4], scaleanchor="x", scaleratio=1), showlegend=False, uirevision='c', margin=dict(l=20, r=20, t=20, b=20))
    return fig, "Status: Valid", {'color': 'green'}

@app.callback(
    [Output('static-plots-sc', 'children'), Output('download-csv-sc', 'data')],
    [Input('btn-plots-sc', 'n_clicks'), Input('btn-download-sc', 'n_clicks')],
    [State('sl-R-sc', 'value'), State('sl-L-sc', 'value'), State('sl-E-sc', 'value')]
)
def update_sc_data(btn_p, btn_d, r, L, e):
    if not ctx.triggered: return dash.no_update, dash.no_update
    trig = ctx.triggered[0]['prop_id']
    if L < r + abs(e): L = r + abs(e) + 0.5

    th2_sw = np.linspace(0, 2*np.pi, 360)
    yA_sw = r * np.sin(th2_sw)
    valid = L >= np.abs(e - yA_sw)
    if not np.any(valid): return dash.no_update, dash.no_update

    th2_v = th2_sw[valid]
    yA_v = r * np.sin(th2_v)
    th3_v = np.arcsin((e - yA_v) / L)
    xB_v = r * np.cos(th2_v) + L * np.cos(th3_v)
    vB = np.gradient(xB_v) / np.gradient(th2_v)
    aB = np.gradient(vB) / np.gradient(th2_v)

    if 'btn-plots-sc' in trig:
        f_v = go.Figure(data=go.Scatter(x=np.rad2deg(th2_v), y=vB, line=dict(color='blue'))); f_v.update_layout(title="Slider Velocity (v_B)", margin=dict(l=20, r=20, t=40, b=20))
        f_a = go.Figure(data=go.Scatter(x=np.rad2deg(th2_v), y=aB, line=dict(color='red'))); f_a.update_layout(title="Slider Accel (a_B)", margin=dict(l=20, r=20, t=40, b=20))
        return [dcc.Graph(figure=f_v, style={'width': '50%'}), dcc.Graph(figure=f_a, style={'width': '50%'})], dash.no_update
    elif 'btn-download-sc' in trig:
        df = pd.DataFrame({'Crank_Angle': np.rad2deg(th2_v), 'Slider_Velocity': vB, 'Slider_Acceleration': aB})
        return dash.no_update, dcc.send_data_frame(df.to_csv, "slidercrank_data.csv", index=False)

# =====================================================================
# 7. RUN SERVER
# =====================================================================
if __name__ == '__main__':
    # Runs the entire master app on a single port!

    app.run(debug=True, port=8060)
