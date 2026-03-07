"""Tests for Campaign aggregate."""

from datetime import datetime
from uuid import uuid4

import pytest

from tic.campaign.domain.campaign import Campaign, SaveAlreadyImported


class TestCampaign:
    """Tests for the Campaign aggregate."""

    def test_campaign_creation_with_explicit_parameters(self) -> None:
        """Test creating a campaign with explicit parameters (for loading from storage)."""
        campaign_id = uuid4()
        name = "ResistCouncil"
        created_at = datetime(2045, 1, 1, 0, 0, 0)

        campaign = Campaign(id=campaign_id, name=name, created_at=created_at)

        assert campaign.id == campaign_id
        assert campaign.name == name
        assert campaign.created_at == created_at

    def test_campaign_factory_method_with_explicit_id_and_timestamp(self) -> None:
        """Test creating a new campaign with explicit id and timestamp (for testability)."""
        name = "ResistCouncil"
        campaign_id = uuid4()
        created_at = datetime(2045, 1, 1, 0, 0, 0)

        campaign = Campaign.create_new(name, id=campaign_id, created_at=created_at)

        assert campaign.name == name
        assert campaign.id == campaign_id
        assert campaign.created_at == created_at

    def test_campaign_factory_method_defaults_to_generated_id_and_system_time(
        self,
    ) -> None:
        """Test creating a new campaign without explicit params generates id and uses system time."""
        name = "ResistCouncil"
        before = datetime.now()

        campaign = Campaign.create_new(name)

        after = datetime.now()

        assert campaign.name == name
        assert campaign.id is not None  # UUID generated
        assert before <= campaign.created_at <= after

    def test_campaign_factory_method_with_explicit_id_only(self) -> None:
        """Test creating a new campaign with explicit id but default timestamp."""
        name = "ResistCouncil"
        campaign_id = uuid4()
        before = datetime.now()

        campaign = Campaign.create_new(name, id=campaign_id)

        after = datetime.now()

        assert campaign.name == name
        assert campaign.id == campaign_id
        assert before <= campaign.created_at <= after

    def test_campaign_factory_method_with_explicit_timestamp_only(self) -> None:
        """Test creating a new campaign with explicit timestamp but generated id."""
        name = "ResistCouncil"
        created_at = datetime(2045, 1, 1, 0, 0, 0)

        campaign = Campaign.create_new(name, created_at=created_at)

        assert campaign.name == name
        assert campaign.id is not None  # UUID generated
        assert campaign.created_at == created_at

    def test_campaign_deduplication_guard_on_same_game_date(self) -> None:
        """Test that importing the same game_date twice raises SaveAlreadyImported."""
        campaign = Campaign.create_new(
            "ResistCouncil", created_at=datetime(2045, 1, 1)
        )

        game_date = datetime(2045, 3, 15, 10, 30, 0)

        # First import should succeed
        campaign.record_save_import(game_date)

        # Second import of the same game_date should raise
        with pytest.raises(SaveAlreadyImported):
            campaign.record_save_import(game_date)

    def test_campaign_allows_different_game_dates(self) -> None:
        """Test that different game_dates can be imported."""
        campaign = Campaign.create_new(
            "ResistCouncil", created_at=datetime(2045, 1, 1)
        )

        game_date_1 = datetime(2045, 3, 15, 10, 30, 0)
        game_date_2 = datetime(2045, 3, 16, 10, 30, 0)

        # Both should succeed
        campaign.record_save_import(game_date_1)
        campaign.record_save_import(game_date_2)

        assert len(campaign.imported_game_dates) == 2
        assert game_date_1 in campaign.imported_game_dates
        assert game_date_2 in campaign.imported_game_dates
