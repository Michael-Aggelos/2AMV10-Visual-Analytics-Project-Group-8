from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import base64
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import plotly.graph_objects as go

shots_df = pd.read_csv("NBA_2004_2023_Shots_2.csv")
# Load the aggregated shots data for plotly court
grouped = pd.read_csv('NBA_Team_Zone_Aggregated_Shots_2023.csv')

# update hexplot court
def update_hexshot_chart(selected_team, selected_season):
    player_shots = shots_df[(shots_df['TEAM_NAME'] == selected_team) & (shots_df['SEASON_2'] == selected_season)]
    
    
    fig, ax = plt.subplots(figsize=(5, 4.7))
    # Set axis limits
    ax.set_xlim(250, -250)
    ax.set_ylim(-47.5, 422.5)

    # Create a hexbin plot
    hb = ax.hexbin(x=player_shots.LOC_X, y=player_shots.LOC_Y, C=player_shots.shot_made,
                    gridsize=40, edgecolors='orange', cmap='Blues')

    # Hide axes
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax = draw_court(ax, outer_lines=True)

    # Show colorbar
    cb = fig.colorbar(hb, ax=ax, orientation='vertical')
    cb.set_label('Accuracy')

    # Invert the x-axis
    ax.invert_xaxis()

    # Convert plot to base64 string
    buffer = io.BytesIO()
    FigureCanvas(fig).print_png(buffer)
    plot_data = base64.b64encode(buffer.getvalue()).decode()

    return {
        'data': [],
        'layout': {
            'images': [{
                'source': 'data:image/png;base64,{}'.format(plot_data),
                'xref': 'paper',
                'yref': 'paper',
                'x': 0,
                'y': 1,
                'sizex': 1,
                'sizey': 1,
                'sizing': 'stretch',
                'opacity': 1,
                'layer': 'below'
            }],
            'xaxis': {
                'showgrid': False, 
                'zeroline': False, 
                'visible': False
            },
            'yaxis': {
                'showgrid': False, 
                'zeroline': False, 
                'visible': False
            },
            'margin': {
                'l': 0,
                'r': 0,
                't': 0,
                'b': 0
            },
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'autosize': True
        }
    }

# draw hexplot court
def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    from matplotlib.patches import Circle, Rectangle, Arc

    if ax is None:
        ax = plt.gca()

    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='dashed')
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)

    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw, bottom_free_throw,
                      restricted, corner_three_a, corner_three_b, three_arc, center_outer_arc, center_inner_arc]

    if outer_lines:
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False)
        court_elements.append(outer_lines)

    for element in court_elements:
        ax.add_patch(element)

    return ax


# update interactive plotly court
def update_plot_shot(selected_team, selected_season):
    fig = go.Figure()
    draw_plotly_court(fig)
    # Filter the data based on the selected team and season
    filtered_df = grouped[(grouped['team_name'] == selected_team) & (grouped['season'] == selected_season)]
    filtered_df = filtered_df.reset_index(drop=True)
    
    max_freq = filtered_df['frequency'].max()  # Determine the max frequency for scaling
    min_freq = filtered_df['frequency'].min()  # Determine the min frequency for scaling
    colorscale = 'YlOrRd'
    
    # Dynamically set cmin and cmax based on the actual data
    marker_cmin = filtered_df['accuracy_percentage'].min()
    marker_cmax = filtered_df['accuracy_percentage'].max()
    
    ticktexts = [str(marker_cmin)+'%', "", str(marker_cmax)+'%']

    xlocs = filtered_df['average_x']
    ylocs = filtered_df['average_y']
    accs_by_hex = filtered_df['accuracy_percentage']
    freq_by_hex = filtered_df['frequency']

    hexbin_text = [
        '<i>Accuracy: </i>' + str(round(accs_by_hex[i], 1)) + '%<BR>'
        '<i>Frequency: </i>' + str(round(freq_by_hex[i], 2))
        for i in range(len(freq_by_hex))
    ]

    # Clear existing traces
    fig.data = []

    # Calculate sizes
    sizes = 10 + (freq_by_hex - min_freq) / (max_freq - min_freq) * 50  # Scale sizes between 10 and 60

    # Add new trace
    fig.add_trace(go.Scatter(
        x=xlocs, y=ylocs, mode='markers', name='markers',
        marker=dict(
            size=sizes,  # Use the calculated sizes
            sizemode='diameter',
            color=accs_by_hex, colorscale=colorscale,
            colorbar=dict(
                thickness=15,
                x=0.84,
                y=0.87,
                yanchor='middle',
                len=0.2,
                title=dict(
                    text="<B>Accuracy</B>",
                    font=dict(
                        size=11,
                        color='#4d4d4d'
                    ),
                ),
                tickvals=[marker_cmin, (marker_cmin + marker_cmax) / 2, marker_cmax],
                ticktext=ticktexts,
                tickfont=dict(
                    size=11,
                    color='#4d4d4d'
                )
            ),
            cmin=marker_cmin, cmax=marker_cmax,
            line=dict(width=1, color='#333333'), symbol='hexagon',
        ),
        text=hexbin_text,
        hoverinfo='text'
    ))

    return fig

# draw plotly court
def draw_plotly_court(fig, fig_width=600, margins=0):

    import numpy as np
        
    def ellipse_arc(x_center=0.0, y_center=0.0, a=10.5, b=10.5, start_angle=0.0, end_angle=2 * np.pi, N=200, closed=False):
        t = np.linspace(start_angle, end_angle, N)
        x = x_center + a * np.cos(t)
        y = y_center + b * np.sin(t)
        path = f'M {x[0]}, {y[0]}'
        for k in range(1, len(t)):
            path += f'L{x[k]}, {y[k]}'
        if closed:
            path += ' Z'
        return path

    fig_height = fig_width * (470 + 2 * margins) / (500 + 2 * margins)
    fig.update_layout(width=fig_width, height=fig_height)

    # Set axes ranges
    fig.update_xaxes(range=[-250 - margins, 250 + margins], fixedrange=False)
    fig.update_yaxes(range=[-52.5 - margins, 417.5 + margins], fixedrange=False)

    threept_break_y = 89.47765084
    three_line_col = "#777777"
    main_line_col = "#777777"

    fig.update_layout(
        # Line Horizontal
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=False,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False,
            fixedrange=False,
        ),
        shapes=[
            dict(
                type="rect", x0=-250, y0=-52.5, x1=250, y1=417.5,
                line=dict(color=main_line_col, width=1),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="rect", x0=-80, y0=-52.5, x1=80, y1=137.5,
                line=dict(color=main_line_col, width=1),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="rect", x0=-60, y0=-52.5, x1=60, y1=137.5,
                line=dict(color=main_line_col, width=1),
                # fillcolor='#333333',
                layer='below'
            ),
            dict(
                type="circle", x0=-60, y0=77.5, x1=60, y1=197.5, xref="x", yref="y",
                line=dict(color=main_line_col, width=1),
                # fillcolor='#dddddd',
                layer='below'
            ),
            dict(
                type="line", x0=-60, y0=137.5, x1=60, y1=137.5,
                line=dict(color=main_line_col, width=1),
                layer='below'
            ),

            dict(
                type="rect", x0=-2, y0=-7.25, x1=2, y1=-12.5,
                line=dict(color="#ec7607", width=1),
                fillcolor='#ec7607',
            ),
            dict(
                type="circle", x0=-7.5, y0=-7.5, x1=7.5, y1=7.5, xref="x", yref="y",
                line=dict(color="#ec7607", width=1),
            ),
            dict(
                type="line", x0=-30, y0=-12.5, x1=30, y1=-12.5,
                line=dict(color="#ec7607", width=1),
            ),

            dict(type="path",
                 path=ellipse_arc(a=40, b=40, start_angle=0, end_angle=np.pi),
                 line=dict(color=main_line_col, width=1), layer='below'),
            dict(type="path",
                 path=ellipse_arc(a=237.5, b=237.5, start_angle=0.386283101, end_angle=np.pi - 0.386283101),
                 line=dict(color=main_line_col, width=1), layer='below'),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-220, y0=-52.5, x1=-220, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=220, y0=-52.5, x1=220, y1=threept_break_y,
                line=dict(color=three_line_col, width=1), layer='below'
            ),

            dict(
                type="line", x0=-250, y0=227.5, x1=-220, y1=227.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=250, y0=227.5, x1=220, y1=227.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=17.5, x1=-80, y1=17.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=27.5, x1=-80, y1=27.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=57.5, x1=-80, y1=57.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=-90, y0=87.5, x1=-80, y1=87.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90, y0=17.5, x1=80, y1=17.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90, y0=27.5, x1=80, y1=27.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90, y0=57.5, x1=80, y1=57.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),
            dict(
                type="line", x0=90, y0=87.5, x1=80, y1=87.5,
                line=dict(color=main_line_col, width=1), layer='below'
            ),

            dict(type="path",
                 path=ellipse_arc(y_center=417.5, a=60, b=60, start_angle=-0, end_angle=-np.pi),
                 line=dict(color=main_line_col, width=1), layer='below'),

        ]
    )
    return True