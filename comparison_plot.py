"""Functions for making the comparison plot."""

import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, HoverTool, TapTool
from bokeh.models.widgets import CheckboxGroup
from bokeh.plotting import figure, show
from bokeh.layouts import gridplot, column
from bokeh.models.callbacks import CustomJS


def comparison_plot(data_dict=None, df=None):
    """Make a comparison plot either from a data_dict or a DataFrame.

    Args:
        data_dict (dict): The keys are the names of different models.
            The values are pd.DataFrames where the index contains the names of
            the parameters and there are three columns:
                - 'params', containing the point estimates
                - 'conf_int_lower', containing the lower bound of the confidence interval
                - 'conf_int_upper', containing the upper bound of the confidence interval

        df (pd.DataFrame): DataFrame with mandatory columns:
            - *model* (str): model name
            - *param_value* (float): point estimate of the parameter value
            - *param_name* (str): name of the parameter (excluding its group)

            Optional columns:
            - *conf_int_lower* (float): lower end of the confidence interval
            - *conf_int_upper* (float): upper end of the confidence interval
            - *param_group* (str): name of the parameter group
                (used for grouping parameters in plots).
            - *color* (str): color
            - *widget_group* (str): groups that can be filtered through the widget

    """
    if df is None:
        df = _convert_res_dicts_to_df(res_dict=data_dict)

    if "param_group" not in df.columns:
        df["param_group"] = "all"
    if "color" not in df.columns:
        df["color"] = "#035096"

    # safety measure to make sure the index
    # gives the position in the arrays
    # that the source data dictionary points to
    safe_df = df.reset_index(drop=True)

    source = ColumnDataSource(safe_df)

    plots = []
    for param_group_name in df["param_group"].unique():
        # create the "canvas"
        param_group_plot = figure(
            title="Comparison Plot of {} Parameters".format(param_group_name.title()),
            y_range=df[df["param_group"] == param_group_name]["param_name"].unique(),
            plot_width=600,
            plot_height=300,
        )

        # add circles representing the parameter value
        point_estimate_glyph = param_group_plot.circle(
            source=source,
            x="param_value",
            y="param_name",
            size=12,
            color="color",
            selection_color="color",
            nonselection_color="color",
            alpha=0.5,
            selection_alpha=0.9,
            nonselection_alpha=0.5,
        )

        # add the confidence_intervals
        # horizontal whiskers not supported in bokeh 1.0.4
        if "conf_int_lower" in df.columns and "conf_int_upper" in df.columns:
            param_group_plot.hbar(
                source=source,
                y="param_name",
                left="conf_int_lower",
                right="conf_int_upper",
                height=0.3,
                alpha=0.0,
                selection_alpha=0.25,
                nonselection_fill_alpha=0.0,
                line_alpha=0.1,
                color="color",
                selection_color="color",
                nonselection_color="color",
            )

        # HoverTool
        tooltips = [("parameter value", "@param_value"), ("model", "@model")]
        hover = HoverTool(renderers=[point_estimate_glyph], tooltips=tooltips)
        param_group_plot.tools.append(hover)

        # TapTool
        tap_js_kwargs = {"source": source}
        with open("tap_callback.js", "r") as f:
            tap_js_code = f.read()
        tap_callback = CustomJS(args=tap_js_kwargs, code=tap_js_code)
        # point_estimate_glyph as only renderer assures that when a point is chosen
        # only that point's model is chosen
        # this makes it impossible to choose models based on clicking confidence bands
        tap = TapTool(renderers=[point_estimate_glyph], callback=tap_callback)
        param_group_plot.tools.append(tap)

        plots.append(param_group_plot)

    # Widget for selecting groups of models
    if "widget_group" in df.columns:
        widget_labels = sorted(df["widget_group"].unique())
        widget_js_kwargs = {'source': source, 'group_list': widget_labels}
        with open('widget_callback.js', 'r') as f:
            widget_js_code = f.read()
        widget_callback = CustomJS(args=widget_js_kwargs, code=widget_js_code)
        cb_group = CheckboxGroup(
            labels=widget_labels,
            active=[0, 1],
            callback=widget_callback)

    grid = gridplot([cb_group] + plots, toolbar_location="right", ncols=1)
    show(grid)


def _convert_res_dicts_to_df(res_dict):
    # To-Do: Add color handling from res_dict!
    df = pd.DataFrame(
        columns=[
            "param_value",
            "conf_int_lower",
            "conf_int_upper",
            "model",
            "param_name",
            "std",
            "color",
        ]
    )

    model_counter = 0
    for model, param_df in res_dict.items():
        ext_param_df = param_df.copy(deep=True)
        ext_param_df["model"] = model
        ext_param_df["param_name"] = ext_param_df.index
        # assuming that upper and lower are 95% CIs and using the 68-95-99.7 rule
        # https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
        ext_param_df["std"] = (
            ext_param_df["conf_int_upper"] - ext_param_df["conf_int_lower"]
        ) / 4
        df = df.append(ext_param_df, sort=False)
        model_counter += 1

    return df
