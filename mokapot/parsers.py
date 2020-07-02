"""
This module contains the parsers for reading in PSMs
"""
import gzip
import logging

import pandas as pd
from tqdm import tqdm

from . import utils
from .dataset import LinearPsmDataset

LOGGER = logging.getLogger(__name__)

# Functions -------------------------------------------------------------------
def read_pin(pin_files):
    """
    Read Percolator input (PIN) tab-delimited files.

    Read PSMs from one or more Percolator Input (PIN), aggregating them
    into a single :py:class:`~mokapot.dataset.LinearPsmDataset`. For
    more details about the PIN file format, see the
    `Percolator documentation <https://github.com/percolator/percolator/
    wiki/Interface#tab-delimited-file-format>`_.

    Specifically, mokapot requires specific columns in the
    tab-delmited files: `specid`, `scannr`, `peptide`, `proteins`, and
    `label`. Note that these column names are insensitive. In addition
    to the required columns, mokapot will look for an `expmass` column,
    which is generated by `Crux <http://crux.ms>`_, but is not
    intended to be a feature.

    Additionally, mokapot does not currently support specifying a
    default direction or feature weights in the PIN file itself.

    Parameters
    ----------
    pin_files : str or tuple of str
        One or more PIN files to read.

    Returns
    -------
    LinearPsmDataset
        A :py:class:`~mokapot.dataset.LinearPsmDataset` object
        containing the PSMs from all of the PIN files.
    """
    logging.info("Parsing PSMs...")
    pin_df = pd.concat([_parse_pin(f) for f in utils.tuplize(pin_files)])

    # Find all of the necessary columns, case-insensitive:
    specid = tuple(c for c in pin_df.columns if c.lower() == "specid")
    peptides = tuple(c for c in pin_df.columns if c.lower() == "peptide")
    proteins = tuple(c for c in pin_df.columns if c.lower() == "proteins")
    labels = tuple(c for c in pin_df.columns if c.lower() == "label")
    other = tuple(c for c in pin_df.columns if c.lower() == "calcmass")
    spectra = tuple(c for c in pin_df.columns
                    if c.lower() in ["scannr", "expmass"])

    nonfeat = sum([specid, spectra, peptides, proteins, labels, other],
                  tuple())

    features = tuple(c for c in pin_df.columns if c not in nonfeat)

    # Check for errors:
    if len(labels) > 1:
        raise ValueError("More than one label column found in pin file.")

    if len(proteins) > 1:
        raise ValueError("More than one protein column found in pin file.")

    if not all([specid, peptides, proteins, labels, spectra]):
        raise ValueError("This PIN format is incompatible with mokapot. Please"
                         " verify that the required columns are present.")

    # Convert labels to the correct format.
    pin_df[labels[0]] = (pin_df[labels[0]] + 1) / 2

    return LinearPsmDataset(psms=pin_df,
                            target_column=labels[0],
                            spectrum_columns=spectra,
                            peptide_columns=peptides,
                            protein_column=proteins[0],
                            feature_columns=features)


# Utility Functions -----------------------------------------------------------
def _parse_pin(pin_file):
    """Parse a Percolator INput formatted file."""
    pin_df = pd.read_csv(pin_file,
                         sep="\t",
                         usecols=lambda x: True,
                         lineterminator='\n',
                         header=None,
                         dtype=str,
                         low_memory=True)
    LOGGER.info("  - Reading PSMs from %s", pin_file)
    pin_df.columns = pin_df.loc[0, :].values
    pin_df.drop(index=0, inplace=True)
    return pin_df.apply(pd.to_numeric, errors="ignore").reset_index()
