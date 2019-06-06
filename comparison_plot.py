"""Functions for making the comparison plot."""

import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, HoverTool, TapTool
from bokeh.plotting import figure, show, output_notebook
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

        df (pd.DataFrame): DataFrame with columns
            *model*, *param_value*, *param_name*, *conf_int_lower*, *conf_int_upper*, *group*

    """
    if df is None:
        df = _convert_res_dicts_to_df(res_dict=data_dict)

    if "group" not in df.columns:
        df["group"] = "all"

    output_notebook()

    # safety measure to make sure the index
    # gives the position in the arrays
    # that the source data dictionary points to
    safe_df = df.reset_index(drop=True)

    source = ColumnDataSource(safe_df)

    plots = []
    for group_name in df["group"].unique():
        # create the "canvas"
        group_plot = figure(
            title="Comparison Plot of {} Parameters".format(group_name.title()),
            y_range=df[df["group"] == group_name]["param_name"].unique(),
            plot_width=600,
            plot_height=300,
        )

        # add circles representing the parameter value
        point_estimate_glyph = group_plot.circle(
            source=source,
            x="param_value",
            y="param_name",
            size=12,
            color="#035096",
            alpha=0.5,
            nonselection_color="#035096",
            selection_color="firebrick",
            nonselection_alpha=0.2,
            selection_alpha=0.7,
        )

        # add the confidence_intervals
        # horizontal whiskers not supported in bokeh 1.0.4
        conf_int_glyph = group_plot.hbar(
            source=source,
            y="param_name",
            left="conf_int_lower",
            right="conf_int_upper",
            height=0.3,
            alpha=0.0,
            nonselection_fill_alpha=0.0,
            selection_alpha=0.25,
            line_alpha=0.1,
        )

        # HoverTool
        tooltips = [("parameter value", "@param_value"), ("model", "@model")]
        hover = HoverTool(renderers=[point_estimate_glyph], tooltips=tooltips)
        group_plot.tools.append(hover)

        # TapTool
        js_kwargs = {"source": source}
        with open("callback.js", "r") as f:
            js_code = f.read()
        js_callback = CustomJS(args=js_kwargs, code=js_code)
        # point_estimate_glyph as only renderer assures that when a point is chosen
        # only that point's model is chosen
        # this makes it impossible to choose models based on clicking confidence bands
        tap = TapTool(renderers=[point_estimate_glyph], callback=js_callback)
        group_plot.tools.append(tap)

        plots.append(group_plot)

    grid = gridplot(plots, toolbar_location="right", ncols=1)
    show(grid)


def _convert_res_dicts_to_df(res_dict):
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
        ext_param_df["color"] = "#035096"
        df = df.append(ext_param_df, sort=False)
        model_counter += 1

    return df
