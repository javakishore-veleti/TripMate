from middleware.core.services.objects import ServicesObjectFactory
from middleware.core.services.service_names import SERVICE_JOURNAL_HAPPENINGS


class HappeningsFacade:
    def __init__(self):
        self._service = ServicesObjectFactory.get_service(SERVICE_JOURNAL_HAPPENINGS)

    def lookup(
        self,
        user_id: str,
        preferences: dict,
        expand: bool = False,
        year: int | None = None,
        month: int | None = None,
    ) -> dict:
        return self._service.lookup(
            user_id=user_id,
            preferences=preferences,
            expand=expand,
            year=year,
            month=month,
        )
