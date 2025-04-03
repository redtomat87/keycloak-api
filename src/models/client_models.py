from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

class ProtocolMapperRepresentation(BaseModel):
    pass

class ResourceServerRepresentation(BaseModel):
    pass

class ClientRepresentation(BaseModel):
    model_config = ConfigDict(
        extra='ignore',
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    # Основные поля
    id: Optional[str] = None
    client_id: Optional[str] = Field(None, alias="clientId")
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None

    # URL-адреса
    root_url: Optional[str] = Field(None, alias="rootUrl")
    admin_url: Optional[str] = Field(None, alias="adminUrl")
    base_url: Optional[str] = Field(None, alias="baseUrl")

    # Флаги
    surrogate_auth_required: Optional[bool] = Field(None, alias="surrogateAuthRequired")
    enabled: Optional[bool] = None
    always_display_in_console: Optional[bool] = Field(None, alias="alwaysDisplayInConsole")
    bearer_only: Optional[bool] = Field(None, alias="bearerOnly")

    # Настройки аутентификации
    client_authenticator_type: Optional[str] = Field(None, alias="clientAuthenticatorType")
    secret: Optional[str] = None
    registration_access_token: Optional[str] = Field(None, alias="registrationAccessToken")

    # Списки
    default_roles: Optional[List[str]] = Field(None, alias="defaultRoles")
    redirect_uris: Optional[List[str]] = Field(None, alias="redirectUris")
    web_origins: Optional[List[str]] = Field(None, alias="webOrigins")
    protocol_mappers: Optional[List[ProtocolMapperRepresentation]] = Field(None, alias="protocolMappers")

    # Настройки потоков OAuth2
    standard_flow_enabled: Optional[bool] = Field(None, alias="standardFlowEnabled")
    implicit_flow_enabled: Optional[bool] = Field(None, alias="implicitFlowEnabled")
    direct_access_grants_enabled: Optional[bool] = Field(None, alias="directAccessGrantsEnabled")
    service_accounts_enabled: Optional[bool] = Field(None, alias="serviceAccountsEnabled")

    # Дополнительные параметры
    attributes: Optional[Dict[str, str]] = None
    access: Optional[Dict[str, bool]] = None
    origin: Optional[str] = None