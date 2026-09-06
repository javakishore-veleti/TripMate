from core.services.impl.auth_impl import AuthService
from core.services.impl.dashboard_places_impl import DashboardPlacesServiceImpl
from core.services.impl.planner_impl import TravelPlannerServiceImpl
from core.services.service_names import (
    SERVICE_AUTH,
    SERVICE_DASHBOARD_PLACES,
    SERVICE_TRAVEL_PLANNER,
)

service_instances = {}
service_names_to_classes = {
    SERVICE_TRAVEL_PLANNER: TravelPlannerServiceImpl,
    SERVICE_AUTH: AuthService,
    SERVICE_DASHBOARD_PLACES: DashboardPlacesServiceImpl,
}


class ServicesObjectFactory:
    @staticmethod
    def get_service(service_name: str):
        if service_name not in service_names_to_classes:
            raise ValueError(f"Service {service_name} not found")
        if service_name not in service_instances:
            service_instances[service_name] = service_names_to_classes[service_name]()
        return service_instances[service_name]
