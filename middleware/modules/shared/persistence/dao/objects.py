from middleware.modules.shared.persistence.dao.dao_names import (
    DAO_APP_SESSION,
    DAO_APP_USER,
    DAO_TRAVEL_REQUEST,
)
from middleware.modules.shared.persistence.dao.impls import (
    AppSessionDaoImpl,
    AppUserDaoImpl,
    TravelRequestDaoImpl,
)

dao_instances = {}
dao_names_to_classes = {
    DAO_APP_USER: AppUserDaoImpl,
    DAO_APP_SESSION: AppSessionDaoImpl,
    DAO_TRAVEL_REQUEST: TravelRequestDaoImpl,
}


class DaoObjectFactory:
    @staticmethod
    def get_dao(name: str):
        if name not in dao_names_to_classes:
            raise ValueError(f"DAO {name} not found")
        if name not in dao_instances:
            dao_instances[name] = dao_names_to_classes[name]()
        return dao_instances[name]
