"""
These tests verify that the aggregatePsmsToPeptides executable works as expected.
"""  # noqa: E501

import pandas as pd
import pytest

from ..helpers.cli import run_mokapot_cli
from ..helpers.utils import file_exist

# Warnings are errors for these tests
pytestmark = pytest.mark.filterwarnings("error")


def test_determinism_same_file(tmp_path, psm_files_4000):
    """Test that two identical mokapot runs produce same results."""

    params = [
        ("--dest_dir", tmp_path),
        ("--subset_max_train", "2500"),
        ("--max_workers", "8"),
        ("--max_iter", "2"),
        "--keep_decoys",
        "--ensemble",
    ]
    run_mokapot_cli(params + [psm_files_4000[0], "--file_root", "run1"])
    run_mokapot_cli(params + [psm_files_4000[0], "--file_root", "run2"])

    assert file_exist(tmp_path, "run1.targets.peptides.csv")
    assert file_exist(tmp_path, "run1.decoys.peptides.csv")
    assert file_exist(tmp_path, "run1.targets.psms.csv")
    assert file_exist(tmp_path, "run1.decoys.psms.csv")

    assert file_exist(tmp_path, "run2.targets.peptides.csv")
    assert file_exist(tmp_path, "run2.decoys.peptides.csv")
    assert file_exist(tmp_path, "run2.targets.psms.csv")
    assert file_exist(tmp_path, "run2.decoys.psms.csv")

    def read_tsv(filename):
        return pd.read_csv(tmp_path / filename, sep="\t")

    df_run1_t_psms = read_tsv("run1.targets.psms.csv")
    df_run2_t_psms = read_tsv("run2.targets.psms.csv")
    pd.testing.assert_frame_equal(df_run1_t_psms, df_run2_t_psms)

    df_run1_t_peptides = read_tsv("run1.targets.peptides.csv")
    df_run2_t_peptides = read_tsv("run2.targets.peptides.csv")
    pd.testing.assert_frame_equal(df_run1_t_peptides, df_run2_t_peptides)

    df_run1_d_psms = read_tsv("run1.decoys.psms.csv")
    df_run2_d_psms = read_tsv("run2.decoys.psms.csv")
    pd.testing.assert_frame_equal(df_run1_d_psms, df_run2_d_psms)

    df_run1_d_peptides = read_tsv("run1.decoys.peptides.csv")
    df_run2_d_peptides = read_tsv("run2.decoys.peptides.csv")
    pd.testing.assert_frame_equal(df_run1_d_peptides, df_run2_d_peptides)


def test_determinism_different_psmid(tmp_path, psm_files_4000):
    """
    Test that two mokapot runs with 2 files where only the SpecIds are changed
    produce same results.
    """

    cmd = [
        ("--dest_dir", tmp_path),
        ("--subset_max_train", "2500"),
        ("--max_workers", "8"),
        ("--max_iter", "2"),
        "--keep_decoys",
        "--ensemble",
    ]

    run_mokapot_cli(cmd + [psm_files_4000[0], "--file_root", "run1"])
    run_mokapot_cli(cmd + [psm_files_4000[1], "--file_root", "run2"])

    assert file_exist(tmp_path, "run1.targets.peptides.csv")
    assert file_exist(tmp_path, "run1.decoys.peptides.csv")
    assert file_exist(tmp_path, "run1.targets.psms.csv")
    assert file_exist(tmp_path, "run1.decoys.psms.csv")

    assert file_exist(tmp_path, "run2.targets.peptides.csv")
    assert file_exist(tmp_path, "run2.decoys.peptides.csv")
    assert file_exist(tmp_path, "run2.targets.psms.csv")
    assert file_exist(tmp_path, "run2.decoys.psms.csv")

    def read_tsv(filename):
        df = pd.read_csv(tmp_path / filename, sep="\t")
        return df.drop("PSMId", axis=1)

    df_run1_t_psms = read_tsv("run1.targets.psms.csv")
    df_run2_t_psms = read_tsv("run2.targets.psms.csv")
    pd.testing.assert_frame_equal(df_run1_t_psms, df_run2_t_psms)

    df_run1_t_peptides = read_tsv("run1.targets.peptides.csv")
    df_run2_t_peptides = read_tsv("run2.targets.peptides.csv")
    pd.testing.assert_frame_equal(df_run1_t_peptides, df_run2_t_peptides)

    df_run1_d_psms = read_tsv("run1.decoys.psms.csv")
    df_run2_d_psms = read_tsv("run2.decoys.psms.csv")
    pd.testing.assert_frame_equal(df_run1_d_psms, df_run2_d_psms)

    df_run1_d_peptides = read_tsv("run1.decoys.peptides.csv")
    df_run2_d_peptides = read_tsv("run2.decoys.peptides.csv")
    pd.testing.assert_frame_equal(df_run1_d_peptides, df_run2_d_peptides)
