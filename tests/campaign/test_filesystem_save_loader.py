"""Tests for FileSystemSaveLoader."""
from __future__ import annotations

import gzip
import json
import shutil
from datetime import datetime
from pathlib import Path

import pytest

from tic.campaign.domain.parsed_save import ParsedSave
from tic.campaign.infrastructure.filesystem_save_loader import FileSystemSaveLoader

FIXTURE = Path(__file__).parent / "fixtures" / "minimal_campaign_save.json"


@pytest.fixture()
def loader() -> FileSystemSaveLoader:
    return FileSystemSaveLoader()


@pytest.fixture()
def gz_fixture(tmp_path: Path) -> Path:
    gz_path = tmp_path / "minimal_campaign_save.gz"
    with FIXTURE.open("rb") as f_in, gzip.open(gz_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    return gz_path


class TestFileSystemSaveLoader:
    def test_loads_json_file(self, loader: FileSystemSaveLoader) -> None:
        result = loader.load(FIXTURE)
        assert isinstance(result, ParsedSave)

    def test_loads_gz_file(self, loader: FileSystemSaveLoader, gz_fixture: Path) -> None:
        result = loader.load(gz_fixture)
        assert isinstance(result, ParsedSave)

    def test_extracts_faction_name(self, loader: FileSystemSaveLoader) -> None:
        result = loader.load(FIXTURE)
        assert result.faction_name == "The Resistance"

    def test_extracts_game_date_from_time_state(self, loader: FileSystemSaveLoader) -> None:
        result = loader.load(FIXTURE)
        assert result.game_date == datetime(2026, 2, 1, 0, 0, 0)

    def test_gz_and_json_produce_identical_result(
        self, loader: FileSystemSaveLoader, gz_fixture: Path
    ) -> None:
        json_result = loader.load(FIXTURE)
        gz_result = loader.load(gz_fixture)
        assert json_result == gz_result

    def test_raises_if_metadata_state_missing(
        self, loader: FileSystemSaveLoader, tmp_path: Path
    ) -> None:
        broken = {"currentID": {"value": 1}, "gamestates": {}}
        broken_path = tmp_path / "broken.json"
        broken_path.write_text(json.dumps(broken), encoding="utf-8-sig")
        with pytest.raises(ValueError):
            loader.load(broken_path)

    def test_raises_if_time_state_missing(
        self, loader: FileSystemSaveLoader, tmp_path: Path
    ) -> None:
        data = {
            "currentID": {"value": 1},
            "gamestates": {
                "PavonisInteractive.TerraInvicta.TIMetadataState": [
                    {"Key": {"value": 1}, "Value": {"playerFactionName": "The Resistance"}}
                ]
            },
        }
        broken_path = tmp_path / "no_time_state.json"
        broken_path.write_text(json.dumps(data), encoding="utf-8-sig")
        with pytest.raises(ValueError):
            loader.load(broken_path)

    def test_unknown_gamestate_keys_are_preserved(self, loader: FileSystemSaveLoader) -> None:
        """All keys in the file are kept — projection layers decide what to use."""
        result = loader.load(FIXTURE)
        assert len(result.gamestates) == 2  # TIMetadataState + TITimeState
