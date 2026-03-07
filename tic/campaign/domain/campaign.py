"""Campaign aggregate and exceptions."""

from datetime import datetime
from uuid import UUID, uuid4


class SaveAlreadyImported(Exception):
    """Raised when attempting to import a save with a game_date already in the campaign."""

    pass


class Campaign:
    """Campaign aggregate root.

    Represents a single Terra Invicta campaign (one faction per TIC instance).
    Guards against duplicate imports by tracking imported game dates.
    """

    def __init__(self, id: UUID, name: str, created_at: datetime) -> None:
        """Initialize a campaign.

        Private constructor. Use Campaign.create_new() to create new campaigns,
        or pass explicit parameters when loading from storage.

        Args:
            id: The campaign UUID (surrogate key for storage).
            name: The campaign name (faction identity, e.g., "ResistCouncil").
            created_at: When the campaign was first imported.
        """
        self.id = id
        self.name = name
        self.created_at = created_at
        self.imported_game_dates: set[datetime] = set()

    @classmethod
    def create_new(
        cls,
        name: str,
        id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> "Campaign":
        """Factory method to create a new campaign.

        Public constructor for new campaigns. Generates a UUID and uses the
        provided created_at timestamp (defaults to system time).

        Args:
            name: The campaign name (faction identity).
            id: Campaign UUID (defaults to uuid4()).
            created_at: When the campaign was created (defaults to now()).

        Returns:
            A new Campaign aggregate.
        """
        return cls(
            id=id or uuid4(),
            name=name,
            created_at=created_at or datetime.now(),
        )

    def record_save_import(self, game_date: datetime) -> None:
        """Record that a save with this game_date has been imported.

        Args:
            game_date: The in-game date of the save being imported.

        Raises:
            SaveAlreadyImported: If this game_date has already been imported.
        """
        if game_date in self.imported_game_dates:
            raise SaveAlreadyImported(
                f"Save with game_date {game_date} already imported for campaign {self.name}"
            )
        self.imported_game_dates.add(game_date)
