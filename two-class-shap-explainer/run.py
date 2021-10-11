# Copyright (c) 2021 Microsoft
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import json
from os import PathLike
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split
import typer
from azureml.core import Run
from azureml.interpret import ExplanationClient
from azureml.studio.core.io.data_frame_directory import \
    load_data_frame_from_directory
from azureml.studio.core.io.model_directory import ModelDirectory
from interpret_community.shap import KernelExplainer

run = Run.get_context()
MAX_FEATURES_UPLOADED = 500


def get_model_schema(model_directory: ModelDirectory) -> dict:
    """Return a dict object that contains the Schema file created by AML Training"""
    with open(model_directory.basedir / model_directory._SCHEMA_FILE_PATH, 'r') as schema_file:
        schema = json.load(schema_file)
    return schema


def get_data(data_path: PathLike, target_column: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = load_data_frame_from_directory(data_path).data

    x_df = df.drop(target_column, axis=1).astype(float)
    y_df = df[target_column].astype(float)

    return x_df, y_df


def get_kernel_explainer_model(model_dir: ModelDirectory, x_df: pd.DataFrame, features: list):
    """Return a trained explainer model"""
    model = model_dir.model.model

    x_norm, _ = model_dir.model.normalizer.transform(x_df, features)

    explainer = KernelExplainer(model, x_norm, features=features)
    return explainer, x_norm


def get_global_explanations(explainer: KernelExplainer, x_df: pd.DataFrame, y_df: pd.DataFrame, sample_size: int = 100):
    """Return a list of global explanations"""

    x_sub, _, y_sub, _ = train_test_split(x_df, y_df, train_size=sample_size, stratify=y_df)

    global_explanations = explainer.explain_global(x_sub, include_local=True)
    return global_explanations, y_sub


def main(
    trained_model_path: Path = typer.Option(..., "--trained-model",
                                            help="Path to the trained model",
                                            file_okay=True,
                                            dir_okay=True,
                                            exists=True),
    sample_data_path: Path = typer.Option(..., "--sample-data",
                                          help="Path to the data used",
                                          file_okay=True,
                                          dir_okay=True,
                                          exists=True),
    target_column: str = typer.Option(..., "--target-column",
                                      help="Column name of the label column"),
    sample_size: int = typer.Option(100, "--sample-size",
                                    help='The number of samples used to generate the global explanation')
):
    model_dir = ModelDirectory.load(trained_model_path)

    schema = get_model_schema(model_dir)
    x_df, y_df = get_data(sample_data_path, target_column)

    column_names = [col['name'] for col in schema['columnAttributes'] if col['name'] != target_column]

    explainer, norm_x = get_kernel_explainer_model(model_dir, x_df, column_names)
    global_explanation, y_sub = get_global_explanations(explainer, norm_x, y_df, sample_size)

    # Save the global explanation to a file
    client = ExplanationClient.from_run(run)

    top_k = min(MAX_FEATURES_UPLOADED, len(column_names))

    client.upload_model_explanation(global_explanation, comment='global_explanation', true_ys=y_sub.values, top_k=top_k)


if __name__ == '__main__':
    typer.run(main)
