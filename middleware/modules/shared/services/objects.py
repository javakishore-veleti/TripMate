from middleware.modules.plans_mgmt.services.journal_happenings_service import JournalHappeningsServiceImpl
from middleware.modules.plans_mgmt.services.planner_service import TravelPlannerServiceImpl
from middleware.modules.shared.services.service_names import (
    SERVICE_AUTH,
    SERVICE_DASHBOARD_PLACES,
    SERVICE_JOURNAL_HAPPENINGS,
    SERVICE_TRAVEL_PLANNER,
)
from middleware.modules.travel_search.services.dashboard_places_service import DashboardPlacesServiceImpl
from middleware.modules.user_mgmt.services.auth_service import AuthService

service_instances = {}
service_names_to_classes = {
    SERVICE_TRAVEL_PLANNER: TravelPlannerServiceImpl,
    SERVICE_AUTH: AuthService,
    SERVICE_DASHBOARD_PLACES: DashboardPlacesServiceImpl,
    SERVICE_JOURNAL_HAPPENINGS: JournalHappeningsServiceImpl,
}


class ServicesObjectFactory:
    @staticmethod
    def get_service(service_name: str):
        if service_name not in service_names_to_classes:
            raise ValueError(f"Service {service_name} not found")
        if service_name not in service_instances:
            service_instances[service_name] = service_names_to_classes[service_name]()
        return service_instances[service_name]
