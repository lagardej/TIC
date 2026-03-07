"""SQLite implementation of CampaignRepository."""
from __future__ import annotations

from tic.campaign.domain.campaign import Campaign
from tic.campaign.domain.campaign_repository import CampaignRepository


class SqliteCampaignRepository(CampaignRepository):
    """SQLite-backed Campaign repository.

    Each campaign is stored as an isolated SQLite database under .tic/campaigns/.
    The campaign registry lives in .tic/tic.db.
    """

    def find_by_faction(self, faction_name: str) -> Campaign | None:
        raise NotImplementedError

    def save(self, campaign: Campaign) -> None:
        raise NotImplementedError
