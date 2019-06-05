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

    if 'group' not in df.columns:
        df['group'] = 'all'

    output_notebook()

    plots = []
    for group_name in df['group'].unique():
        group_df = df[df['group'] == group_name]
        source = ColumnDataSource(group_df)
        group_plot = figure(
            title="Comparison Plot of {} Parameters".format(group_name.title()),
            y_range=sorted(group_df["param_name"].unique(), reverse=True),
            toolbar_location="right",
            plot_width=600,
            plot_height=300,
            tools="pan,wheel_zoom,box_zoom,box_select,tap,reset,save",
        )
        group_plot.grid.grid_line_alpha = 0
        group_plot.hbar(
            "param_name",
            left="lower",
            right="upper",
            height=0.3,
            fill_alpha=0.2,
            nonselection_fill_alpha=0,
            line_color=None,
            source=source,
        )
        circle_glyph = group_plot.circle(
            "param_value",
            "param_name",
            fill_color="#035096",
            selection_fill_color="firebrick",
            nonselection_fill_alpha=0.2,
            size=8,
            source=source,
        )

        tooltips = [
            ("parameter value", "@param_value"),
            ("confidence interval", "(@lower{(0.000)}, @upper{(0.000)})"),
            ("model", "@model"),
            # ("standard deviation", "@std{(0.0000)}"),
        ]
        hover = HoverTool(renderers=[circle_glyph], tooltips=tooltips)
        group_plot.tools.append(hover)
        plots.append(group_plot)

    p = gridplot(plots, toolbar_location="right", ncols=1)
    return show(p)


def _convert_res_dicts_to_df(res_dict):
    df = pd.DataFrame(
        columns=["param_value", "lower", "upper", "model", "param_name", "std", "color"]
    )

    model_counter = 0
    for model, param_df in res_dict.items():
        ext_param_df = param_df.copy(deep=True)
        ext_param_df["model"] = model
        ext_param_df["param_name"] = ext_param_df.index
        # assuming that upper and lower are 95% CIs and using the 68-95-99.7 rule
        # https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
        ext_param_df["std"] = (ext_param_df["upper"] - ext_param_df["lower"]) / 4
        ext_param_df["color"] = "mediumelectricblue"
        df = df.append(ext_param_df, sort=False)
        model_counter += 1

    return df
