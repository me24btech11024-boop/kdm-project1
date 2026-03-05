import dash
from dash import dcc, html, ctx
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import numpy as np
import pandas as pd

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Universal Kinematics Dashboard"
server = app.server 

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# =====================================================================
# PAGE LAYOUTS (Removed the dcc.Interval loops!)
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
            html.Label("Animation Speed"), dcc.Slider(id='sl-speed-4b', min=1, max=10, step=1, value=5),
            html.Hr(),
            html.Button("📊 Generate Plots", id="btn-plots-4b", n_clicks=0, style={'width': '100%', 'padding': '10px', 'marginBottom': '10px'}),
            html.Button("💾 Download CSV", id="btn-download-4b", n_clicks=0, style={'width': '100%', 'padding': '10px', 'backgroundColor': '#4CAF50', 'color': 'white'}),
            dcc.Download(id="download-csv-4b")
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
            html.Label("Animation Speed"), dcc.Slider(id='sl-speed-sc', min=1, max=10, step=1, value=5),
            html.Hr(),
            html.Button("📊 Generate Plots", id="btn-plots-sc", n_clicks=0, style={'width': '100%', 'padding': '10px', 'marginBottom': '10px'}),
            html.Button("💾 Download CSV", id="btn-download-sc", n_clicks=0, style={'width': '100%', 'padding': '10px', 'backgroundColor': '#4CAF50', 'color': 'white'}),
            dcc.Download(id="download-csv-sc")
        ]),
        html.Div(style={'width': '70%', 'padding': '0px', 'display': 'flex', 'flexDirection': 'column', 'height': '100vh'}, children=[
            html.Div(style={'height': '60%'}, children=[dcc.Graph(id='live-graph-sc', style={'height': '100%'})]),
            html.Div(id='static-plots-sc', style={'height': '40%', 'display': 'flex', 'flexDirection': 'row', 'backgroundColor': '#f1f1f1'})
        ])
    ])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/fourbar': return layout_4bar()
    elif pathname == '/slidercrank': return layout_slider()
    return layout_home()

# =====================================================================
# FOUR-BAR CLIENT-SIDE ANIMATION CALLBACK
# =====================================================================
@app.callback(
    [Output('live-graph-4b', 'figure'), Output('status-text-4b', 'children'), Output('status-text-4b', 'style')],
    [Input('sl-L1-4b', 'value'), Input('sl-L2-4b', 'value'), Input('sl-L3-4b', 'value'), Input('sl-L4-4b', 'value'), Input('sl-CpL-4b', 'value'), Input('sl-CpA-4b', 'value'), Input('sl-speed-4b', 'value')]
)
def update_4b_anim(L1, L2, L3, L4, CpL, CpA_deg, speed):
    min_other = min(L1, L3, L4)
    if L2 > min_other - 0.5: L2 = max(1.0, min_other - 0.5)
    CpA = np.deg2rad(CpA_deg)
    
    links = sorted([L1, L2, L3, L4])
    is_grashof = links[0] + links[3] < links[1] + links[2]
    status = "Status: Grashof" if is_grashof else "Status: Non-Grashof"
    
    # 180 points keeps the math light but the animation incredibly smooth
    th2_sw = np.linspace(0, 2*np.pi, 180)
    xA_sw, yA_sw = L2 * np.cos(th2_sw), L2 * np.sin(th2_sw)
    dist_sw = np.sqrt((L1 - xA_sw)**2 + (-yA_sw)**2)
    valid = (dist_sw <= (L3 + L4)) & (dist_sw >= abs(L3 - L4))
    
    fig = go.Figure()
    if not np.any(valid): return fig, "Cannot Assemble", {'color': 'red'}

    th2_v = th2_sw[valid]
    xA_v, yA_v, d_v = xA_sw[valid], yA_sw[valid], dist_sw[valid]
    th3_v = np.arctan2(-yA_v, L1 - xA_v) - np.arccos((L3**2 + d_v**2 - L4**2) / (2 * L3 * d_v))
    xB_v, yB_v = xA_v + L3 * np.cos(th3_v), yA_v + L3 * np.sin(th3_v)
    xP_v, yP_v = xA_v + CpL * np.cos(th3_v + CpA), yA_v + CpL * np.sin(th3_v + CpA)

    # Base Traces (Frame 0)
    fig.add_trace(go.Scatter(x=xP_v, y=yP_v, mode='lines', line=dict(color='cyan', dash='dash'), name='Trace')) # Trace 0
    fig.add_trace(go.Scatter(x=[0, L1], y=[0, 0], mode='lines+markers', line=dict(color='black', width=5), marker=dict(size=10))) # Trace 1
    fig.add_trace(go.Scatter(x=[0, xA_v[0]], y=[0, yA_v[0]], mode='lines+markers', line=dict(color='red', width=5), marker=dict(size=10))) # Trace 2
    fig.add_trace(go.Scatter(x=[xA_v[0], xB_v[0]], y=[yA_v[0], yB_v[0]], mode='lines+markers', line=dict(color='green', width=5), marker=dict(size=10))) # Trace 3
    fig.add_trace(go.Scatter(x=[L1, xB_v[0]], y=[0, yB_v[0]], mode='lines+markers', line=dict(color='blue', width=5), marker=dict(size=10))) # Trace 4
    fig.add_trace(go.Scatter(x=[xA_v[0], xB_v[0], xP_v[0], xA_v[0]], y=[yA_v[0], yB_v[0], yP_v[0], yA_v[0]], fill='toself', fillcolor='rgba(0, 255, 255, 0.4)', line=dict(color='rgba(255,255,255,0)'))) # Trace 5

    # Build the Flipbook Frames
    frames = []
    indices = list(range(len(th2_v)))
    if not is_grashof: indices = indices + indices[-2:0:-1] # Rock back and forth

    for i in indices:
        frames.append(go.Frame(
            data=[
                go.Scatter(x=[0, xA_v[i]], y=[0, yA_v[i]]),
                go.Scatter(x=[xA_v[i], xB_v[i]], y=[yA_v[i], yB_v[i]]),
                go.Scatter(x=[L1, xB_v[i]], y=[0, yB_v[i]]),
                go.Scatter(x=[xA_v[i], xB_v[i], xP_v[i], xA_v[i]], y=[yA_v[i], yB_v[i], yP_v[i], yA_v[i]])
            ],
            traces=[2, 3, 4, 5] # Only update the moving parts!
        ))
    fig.frames = frames

    # Layout with Play/Pause
    anim_speed = max(10, 100 - (speed * 8)) # Scales the speed slider to JS milliseconds
    mr = max([L1, L2, L3, L4]) * 2.5
    fig.update_layout(
        xaxis=dict(range=[-mr/2, L1 + mr/2]), yaxis=dict(range=[-mr/2, mr/2], scaleanchor="x", scaleratio=1), 
        showlegend=False, margin=dict(l=20, r=20, t=60, b=20),
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.0, y=1.1, xanchor="left", yanchor="top", direction="right",
            buttons=[
                dict(label="▶️ Play", method="animate", args=[None, dict(frame=dict(duration=anim_speed, redraw=False), fromcurrent=True, transition=dict(duration=0), mode="immediate")]),
                dict(label="⏸️ Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))])
            ]
        )]
    )
    return fig, status, {'color': 'green'} if is_grashof else {'color': 'red'}

# =====================================================================
# SLIDER-CRANK CLIENT-SIDE ANIMATION CALLBACK
# =====================================================================
@app.callback(
    [Output('live-graph-sc', 'figure'), Output('status-text-sc', 'children'), Output('status-text-sc', 'style')],
    [Input('sl-R-sc', 'value'), Input('sl-L-sc', 'value'), Input('sl-E-sc', 'value'), Input('sl-speed-sc', 'value')]
)
def update_sc_anim(r, L, e, speed):
    if L < r + abs(e): L = r + abs(e) + 0.5
    
    th2_sw = np.linspace(0, 2*np.pi, 180)
    yA_sw = r * np.sin(th2_sw)
    valid = L >= np.abs(e - yA_sw)
    
    fig = go.Figure()
    if not np.any(valid): return fig, "Cannot Assemble", {'color': 'red'}

    th2_v = th2_sw[valid]
    xA_v, yA_v = r * np.cos(th2_v), r * np.sin(th2_v)
    th3_v = np.arcsin((e - yA_v) / L)
    xB_v = xA_v + L * np.cos(th3_v)
    
    # Base Traces
    fig.add_trace(go.Scatter(x=[-(r+L+5), r+L+5], y=[e, e], mode='lines', line=dict(color='black', dash='dash'))) # Trace 0
    fig.add_trace(go.Scatter(x=[0, xA_v[0]], y=[0, yA_v[0]], mode='lines+markers', line=dict(color='red', width=5), marker=dict(size=10))) # Trace 1
    fig.add_trace(go.Scatter(x=[xA_v[0], xB_v[0]], y=[yA_v[0], e], mode='lines+markers', line=dict(color='green', width=5), marker=dict(size=10))) # Trace 2
    bx = xB_v[0]
    fig.add_trace(go.Scatter(x=[bx-1.5, bx+1.5, bx+1.5, bx-1.5, bx-1.5], y=[e-1, e-1, e+1, e+1, e-1], fill='toself', fillcolor='rgba(0, 0, 255, 0.4)', line=dict(color='blue'))) # Trace 3

    # Build the Flipbook Frames
    frames = []
    for i in range(len(th2_v)):
        cx, cy, bx_i = xA_v[i], yA_v[i], xB_v[i]
        frames.append(go.Frame(
            data=[
                go.Scatter(x=[0, cx], y=[0, cy]),
                go.Scatter(x=[cx, bx_i], y=[cy, e]),
                go.Scatter(x=[bx_i-1.5, bx_i+1.5, bx_i+1.5, bx_i-1.5, bx_i-1.5], y=[e-1, e-1, e+1, e+1, e-1])
            ],
            traces=[1, 2, 3]
        ))
    fig.frames = frames

    anim_speed = max(10, 100 - (speed * 8))
    fig.update_layout(
        xaxis=dict(range=[-(r+L+2), r+L+5]), yaxis=dict(range=[min(-r, e-2)-4, max(r, e+2)+4], scaleanchor="x", scaleratio=1), 
        showlegend=False, margin=dict(l=20, r=20, t=60, b=20),
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.0, y=1.1, xanchor="left", yanchor="top", direction="right",
            buttons=[
                dict(label="▶️ Play", method="animate", args=[None, dict(frame=dict(duration=anim_speed, redraw=False), fromcurrent=True, transition=dict(duration=0), mode="immediate")]),
                dict(label="⏸️ Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))])
            ]
        )]
    )
    return fig, "Status: Valid", {'color': 'green'}

# =====================================================================
# DATA EXPORT & PLOTS CALLBACKS
# =====================================================================
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

if __name__ == '__main__':
    app.run(debug=False)
