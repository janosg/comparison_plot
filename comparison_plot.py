"""Functions for making the comparison plot."""

import pandas as pd
import numpy as np

def comparison_plot(data_dict):
    """Make a comparison plot.

    Args:
        data_dict (dict): The keys are the names of different models.
            The values are pd.DataFrames where the index contains the names of
            the parameters and there are three columns:
                - 'params', containing the point estimates
                - 'lower', containing the lower bound of the confidence interval
                - 'upper', containing the upper bound of the confidence interval

    """
    from bokeh.models import ColumnDataSource, HoverTool, Circle
    from bokeh.plotting import figure, show, output_notebook
    from bokeh.layouts import gridplot, column

    # Make new DataFrame to link graphs with ColumnDataSource

    dic = data_dict.copy()

    for value in dic.values():
        M = len(value.index)

    N = len(dic)

    params = []
    lower = []
    upper = []
    parameter_lists = [[] for i in range(M)]
    param_name = []
    stds_list = []
    model = []

    for key, value in dic.items():
        model.append(key)
        param_name = value.index
        params.append(value["params"])
        lower.append(value["lower"])
        upper.append(value["upper"])
        for i in range(M):
            parameter_lists[i].append(value["params"][i])

    for i in range(M):
        stds_list.append(np.std(parameter_lists[i]))

    params = np.array(params)
    params = params.ravel()
    lower = np.array(lower)
    lower = lower.ravel()
    upper = np.array(upper)
    upper = upper.ravel()
    param_name = list(param_name)
    models = np.repeat(model, M)
    param_names = np.array(param_name * N)
    stds = np.array(stds_list * N)

    s = pd.DataFrame(
        {
            "params": params,
            "stds": stds,
            "lower": lower,
            "upper": upper,
            "models": models,
            "param_names": param_names,
        }
    )

    # Make plot
    options = dict(
        plot_width=600,
        plot_height=300,
        tools="pan,wheel_zoom,box_zoom,box_select,tap,reset,save",
    )
    source = ColumnDataSource(s)
    output_notebook()

    # Make plot with model and parameter names
    p0 = figure(
        title="Models",
        x_range=model,
        y_range=param_name,
        toolbar_location="right",
        plot_width=600,
        plot_height=150,
        tools="pan,wheel_zoom,box_zoom,box_select,tap,reset,save",
    )
    p0.grid.grid_line_alpha = 0
    p0.circle("models", "param_names", fill_color="salmon", size=8, source=source)

    # Make plot with estimates and parameter names
    TOOLTIPS = [
        ("parameter value", "@params"),
        ("confidence interval", "(@lower{(0.000)}, @upper{(0.000)})"),
        ("model", "@models"),
        ("standard deviation", "@stds{(0.0000)}"),
    ]

    p1 = figure(
        title="Comparison Plot", y_range=param_name, toolbar_location="right", **options
    )
    p1.grid.grid_line_alpha = 0
    p1.hbar(
        "param_names",
        left="lower",
        right="upper",
        height=0.3,
        fill_alpha=0.2,
        nonselection_fill_alpha=0,
        line_color=None,
        source=source,
    )
    circle_glyph = p1.circle(
        "params",
        "param_names",
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
