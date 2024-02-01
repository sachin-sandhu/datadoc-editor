from __future__ import annotations

import copy
import datetime
import pathlib
from dataclasses import dataclass
from pathlib import PurePath

import pytest

from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo
from datadoc.enums import DatasetState
from tests.utils import TEST_PARQUET_FILEPATH


@dataclass
class DatasetPathTestCase:
    """Structure to define attributes needed for a test case."""

    path: str
    expected_contains_data_from: datetime.date
    expected_contains_data_until: datetime.date


TEST_CASES = [
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-10-01_p2022-12-31_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 10, 1),
        expected_contains_data_until=datetime.date(2022, 12, 31),
    ),
    DatasetPathTestCase(
        path="grensehandel_imputert_p2022-10_p2022-12_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 10, 1),
        expected_contains_data_until=datetime.date(2022, 12, 31),
    ),
    DatasetPathTestCase(
        path="flygende_objekter_p2019_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2019, 12, 31),
    ),
    DatasetPathTestCase(
        path="framskrevne-befolkningsendringer_p2019_p2050_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2050, 12, 31),
    ),
    DatasetPathTestCase(
        path="ufo_observasjoner_p2019_p2020_v1.parquet",
        expected_contains_data_from=datetime.date(2019, 1, 1),
        expected_contains_data_until=datetime.date(2020, 12, 31),
    ),
    DatasetPathTestCase(
        path="omsetning_p2020W15_v1.parquet",
        expected_contains_data_from=datetime.date(2020, 4, 6),
        expected_contains_data_until=datetime.date(2020, 4, 12),
    ),
    DatasetPathTestCase(
        path="omsetning_p1981-W52_v1.parquet",
        expected_contains_data_from=datetime.date(1981, 12, 21),
        expected_contains_data_until=datetime.date(1981, 12, 27),
    ),
    DatasetPathTestCase(
        path="personinntekt_p2022H1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 6, 30),
    ),
    DatasetPathTestCase(
        path="nybilreg_p2022T1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 4, 30),
    ),
    DatasetPathTestCase(
        path="varehandel_p2018Q1_p2018Q4_v1.parquet",
        expected_contains_data_from=datetime.date(2018, 1, 1),
        expected_contains_data_until=datetime.date(2018, 12, 31),
    ),
    DatasetPathTestCase(
        path="pensjon_p2018Q1_v1.parquet",
        expected_contains_data_from=datetime.date(2018, 1, 1),
        expected_contains_data_until=datetime.date(2018, 3, 31),
    ),
    DatasetPathTestCase(
        path="skipsanloep_p2021B2_v1.parquet",
        expected_contains_data_from=datetime.date(2021, 3, 1),
        expected_contains_data_until=datetime.date(2021, 4, 30),
    ),
    DatasetPathTestCase(
        path="skipsanloep_p2022B1_v1.parquet",
        expected_contains_data_from=datetime.date(2022, 1, 1),
        expected_contains_data_until=datetime.date(2022, 2, 28),
    ),
]


@pytest.fixture(
    ids=[tc.path for tc in TEST_CASES],
    params=TEST_CASES,
)
def test_data(request: pytest.FixtureRequest) -> DatasetPathTestCase:
    return request.param


@pytest.fixture()
def dataset_path(test_data: DatasetPathTestCase) -> DaplaDatasetPathInfo:
    return DaplaDatasetPathInfo(test_data.path)


@pytest.fixture()
def expected_contains_data_from(test_data: DatasetPathTestCase) -> datetime.date:
    return test_data.expected_contains_data_from


@pytest.fixture()
def expected_contains_data_until(test_data: DatasetPathTestCase) -> datetime.date:
    return test_data.expected_contains_data_until


def test_extract_period_info_date_from(
    dataset_path: DaplaDatasetPathInfo,
    expected_contains_data_from: datetime.date,
):
    assert dataset_path.contains_data_from == expected_contains_data_from


def test_extract_period_info_date_until(
    dataset_path: DaplaDatasetPathInfo,
    expected_contains_data_until: datetime.date,
):
    assert dataset_path.contains_data_until == expected_contains_data_until


@pytest.mark.parametrize(
    "data",
    [
        "nonsen.data",
        "nonsens2.parquet",
        TEST_PARQUET_FILEPATH.name,
    ],
)
def test_extract_period_info_no_period_info_in_path(data: str):
    assert DaplaDatasetPathInfo(data).contains_data_from is None


@pytest.fixture()
def full_dataset_state_path(
    dataset_state_path: str,
) -> pathlib.PurePath:
    """Create a longer path structure from just one section.

    Examples:
    >>> full_dataset_state_path('inndata')
    'tests/inndata/resources/person_data_v1.parquet'
    """
    split_path = list(PurePath(TEST_PARQUET_FILEPATH).parts)
    new_path = copy.copy(split_path)
    new_path.insert(-2, dataset_state_path)
    return PurePath().joinpath(*new_path)


@pytest.mark.parametrize(
    ("dataset_state_path", "expected_result"),
    [
        ("kildedata", DatasetState.SOURCE_DATA),
        ("inndata", DatasetState.INPUT_DATA),
        ("roskildedata/klargjorte-data", DatasetState.PROCESSED_DATA),
        ("klargjorte_data", DatasetState.PROCESSED_DATA),
        ("klargjorte-data", DatasetState.PROCESSED_DATA),
        ("statistikk", DatasetState.STATISTICS),
        ("", None),
    ],
)
def test_get_dataset_state(
    full_dataset_state_path: pathlib.Path,
    expected_result: DatasetState,
):
    actual_state = DaplaDatasetPathInfo(full_dataset_state_path).dataset_state
    assert actual_state == expected_result


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("person_data_v1", "1"),
        ("person_data_v2", "2"),
        ("person_data_vwrong", None),
        ("person_data", None),
        ("person_testdata_p2021-12-31_p2021-12-31_v20", "20"),
    ],
)
def test_get_dataset_version(
    path: str,
    expected: str | None,
):
    assert DaplaDatasetPathInfo(path).dataset_version == expected


# These tests covers both date until after date from, mix of SSB keys and invalid SSB keys
@pytest.mark.parametrize(
    "dataset_path_name",
    [
        "ufo_observasjoner_p2019_p1920_v1.parquet",
        "varehandel_p2018H2_p2018H1_v1.parquet",
        "varehandel_p2018Q1_p2018H2_v1.parquet",
        "sykkeltransport_p1973B8_v1.parquet",
    ],
)
def test_extract_period_info_date_from_invalid_pathname(dataset_path_name: str) -> None:
    dataset = DaplaDatasetPathInfo(dataset_path_name)
    assert dataset.contains_data_from is None


@pytest.mark.parametrize(
    "dataset_path_name",
    [
        "ufo_observasjoner_p2019_p1920_v1.parquet",
        "varehandel_p2018H2_p2018H1_v1.parquet",
        "varehandel_p2018Q1_p2018H2_v1.parquet",
        "sykkeltransport_p1973B2_p2020T8_v1.parquet",
    ],
)
def test_extract_period_info_date_until_invalid_pathname(
    dataset_path_name: str,
) -> None:
    dataset = DaplaDatasetPathInfo(dataset_path_name)
    assert dataset.contains_data_until is None
