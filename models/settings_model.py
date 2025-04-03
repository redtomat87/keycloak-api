from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    
    keycloak_url: str = ''
    realm_name: str = ''
    client_id: str = ''
    password: str = ''
    page_size: int = 10
    page: int = 0
    username: str = ''
    
    @computed_field
    @property
    def users_url(self) -> str:
        return f'{self.keycloak_url}/admin/realms/{self.realm_name}/users'

    @computed_field
    @property
    def token_url(self) -> str:
        return f'{self.keycloak_url}/realms/{self.realm_name}/protocol/openid-connect/token'

    @computed_field
    @property
    def groups_url(self) -> str:
        return f'{self.keycloak_url}/admin/realms/{self.realm_name}/groups'

    @computed_field
    @property
    def client_scopes_url(self) -> str:
        return f'{self.keycloak_url}/admin/realms/{self.realm_name}/client-scopes'

    users_file_path: str = str(BASE_DIR / 'list_of_users.json')
    token_file_path: str = str(BASE_DIR / 'token_file.json')
    certs_validation_file_path: str = str(BASE_DIR / 'certs_validation.json')
    
    request_timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
        gt=0
    )
    
    @computed_field
    @property
    def users_url_query_params(self) -> Dict[str, Any]:
        return {
            'max': self.page_size,
            'first': self.page,
            'briefRepresentation': 'True'
        }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="KCE_",
        case_sensitive=False,
        extra="ignore",
        validate_default=True
    )

try:
    config = Settings()
except Exception as e:
    print(f"Configuration error: {str(e)}")
    exit(1)
