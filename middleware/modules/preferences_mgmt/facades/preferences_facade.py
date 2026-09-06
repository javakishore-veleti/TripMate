from middleware.modules.preferences_mgmt.services import store


class PreferencesFacade:
    def list_skills(self, user_id: str):
        return store.list_skills(user_id)

    def get_skill(self, user_id: str, slug: str):
        return store.get_skill(user_id, slug)

    def create_skill(self, user_id: str, name: str, description: str, sections: dict):
        return store.create_skill(user_id, name, description, sections)

    def update_skill(self, user_id: str, slug: str, name: str, description: str, sections: dict):
        return store.update_skill(user_id, slug, name, description, sections)

    def delete_skill(self, user_id: str, slug: str):
        return store.delete_skill(user_id, slug)

    def set_selected(self, user_id: str, ids: list[str]):
        return store.set_selected(user_id, ids)

    @property
    def max_selected(self) -> int:
        return store.MAX_SELECTED
