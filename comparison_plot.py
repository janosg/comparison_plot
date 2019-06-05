"""Functions for making the comparison plot."""

import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, HoverTool, Circle
from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import gridplot, column

def comparison_plot(data_dict=None, df=None):
    """Make a comparison plot either from a data_dict or a DataFrame.

    Args:
        data_dict (dict): The keys are the names of different models.
            The values are pd.DataFrames where the index contains the names of
            the parameters and there are three columns:
                - 'params', containing the point estimates
                - 'lower', containing the lower bound of the confidence interval
                - 'upper', containing the upper bound of the confidence interval

        df (pd.DataFrame): DataFrame with columns
            *model*, *param_value*, *param_name*, *lower*, *upper*, *group*

    """
    if df is None:
        df = _convert_res_dicts_to_df(res_dict=data_dict)
    source = ColumnDataSource(df)

    output_notebook()

    # Make plot with model and parameter names
    p0 = figure(
        title="Models",
        x_range=sorted(df['model'].unique(), reverse=True),
        y_range=df['param_name'].unique().tolist(),
        toolbar_location="right",
        plot_width=600,
        plot_height=150,
        tools="pan,wheel_zoom,box_zoom,box_select,tap,reset,save",
    )
    p0.grid.grid_line_alpha = 0
    p0.circle("model", "param_name", fill_color="salmon", size=8, source=source)

    # Make plot with estimates and parameter names
    TOOLTIPS = [
        ("parameter value", "@params"),
        ("confidence interval", "(@lower{(0.000)}, @upper{(0.000)})"),
        ("model", "@models"),
        ("standard deviation", "@stds{(0.0000)}"),
    ]

    options = dict(
        plot_width=600,
        plot_height=300,
        tools="pan,wheel_zoom,box_zoom,box_select,tap,reset,save",
    )

    p1 = figure(
        title="Comparison Plot", y_range=df['param_name'].unique().tolist(),
        toolbar_location="right", **options
    )
    p1.grid.grid_line_alpha = 0
    p1.hbar(
        "param_name",
        left="lower",
        right="upper",
        height=0.3,
        fill_alpha=0.2,
        nonselection_fill_alpha=0,
        line_color=None,
        source=source,
    )
    circle_glyph = p1.circle(
        "param_value",
        "param_name",
        fill_color="blue",
        selection_fill_color="green",
        nonselection_fill_alpha=0.2,
        size=8,
        source=source,
    )
    hover = HoverTool(renderers=[circle_glyph], tooltips=TOOLTIPS)
    p1.tools.append(hover)

    # Make gridplot with both plots
    p = gridplot([p0, p1], toolbar_location="right", ncols=1)

    return show(p)



def _convert_res_dicts_to_df(res_dict):
    df = pd.DataFrame(
        columns=['param_value', 'lower', 'upper', 'model', 'param_name', 'std', 'color'])

    model_counter = 0
    for model, param_df in res_dict.items():
        ext_param_df = param_df.copy(deep=True)
        ext_param_df['model'] = model
        ext_param_df['param_name'] = ext_param_df.index
        # assuming that upper and lower are 95% CIs and using the 68-95-99.7 rule
        # https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
        ext_param_df['std'] = (ext_param_df['upper'] - ext_param_df['lower']) / 4
        ext_param_df['color'] = "mediumelectricblue"
        df = df.append(ext_param_df, sort=False)
        model_counter += 1

    return df