import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

# Ensure Kaleido uses the correct Chrome executable
pio.kaleido.scope.chromium_executable = "/usr/bin/google-chrome"

def generate_polar_chart(scores, accountid):
    categories = list(scores.keys())
    values = list(scores.values())
    num_vars = len(categories)
    angles = np.linspace(0, 360, num_vars, endpoint=False)

    final_colors = [
        "#F9FE70", #3
        "#98CAFF", #2
        "#20E6EC", #1
        "#CCABFE", #7
        "#FED7BA", #6
        "#8CF4A9", #5
        "#BBCFFD"  #4
    ]

    min_val = min(values)
    max_val = max(values)
    desired_min_thickness = 10
    desired_max_thickness = 1000

    def normalize_value(v):
        if max_val == min_val:
            return desired_max_thickness
        return desired_min_thickness + (v - min_val)/(max_val - min_val) * (desired_max_thickness - desired_min_thickness)

    slice_width = 360 / num_vars
    base_radius = 1000

    fig = go.Figure()

    for i, val in enumerate(values):
        val_thickness = normalize_value(val)
        angle = angles[i]

        fig.add_trace(go.Barpolar(
            r=[base_radius + val_thickness],
            base=[base_radius],
            theta=[angle],
            width=[slice_width],
            marker_color=final_colors[i],
            marker_line_width=0,
            hoverinfo='none',
            opacity=0.66
        ))

    fig.update_layout(
        template=None,
        paper_bgcolor="white",
        plot_bgcolor="white",
        polar=dict(
            bgcolor="white",
            angularaxis=dict(rotation=-13.9, showline=False, showgrid=False, ticks='', showticklabels=False),
            radialaxis=dict(showline=False, showgrid=False, ticks='', showticklabels=False, visible=False)
        ),
        showlegend=False,
        margin=dict(l=250, r=250, t=250, b=250)
    )

    fig.update_layout(
        template=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            angularaxis=dict(showline=False, showgrid=False, ticks='', showticklabels=False),
            radialaxis=dict(showline=False, showgrid=False, ticks='', showticklabels=False, visible=False)
        ),
        showlegend=False,
        margin=dict(l=250, r=250, t=250, b=250)
    )

    # Save the chart as an image
    fig.write_image(accountid, width=1000, height=1000)
