# app/tenants/registry.py
import os
from typing import Dict, Optional
from app.tenants.base import BaseTenant
from app.tenants.clinica import ClinicaTenant
from app.tenants.padaria import PadariaTenant
from app.services.rag_service import rag_service

class TenantRegistry:
    """
    Catálogo central de todas as empresas cadastradas na plataforma.
    """
    def __init__(self) -> None:
        self._tenants: Dict[str, BaseTenant] = {}
        self._carregar_tenants_iniciais()

    def _carregar_tenants_iniciais(self) -> None:
        """Apenas instancia e registra as classes de tenant."""
        try:
            self.register_tenant(ClinicaTenant())
            self.register_tenant(PadariaTenant())
        except Exception as error:
            print(f"[ERRO REGISTRY] Falha ao registrar tenants iniciais: {error}")

    def inicializar_todos_os_rags(self) -> None:
        """
        Executa a indexação dos documentos de cada tenant.
        Chamado de forma controlada durante o startup do servidor.
        """
        for tenant_id, tenant in self._tenants.items():
            caminho_documentos = os.path.join("data", "tenants", tenant_id)
            if os.path.exists(caminho_documentos):
                store_name = rag_service.upload_tenant_documents(
                    tenant_id=tenant_id,
                    documents_dir=caminho_documentos
                )
                if store_name:
                    tenant._file_search_store_id = store_name

    def register_tenant(self, tenant: BaseTenant) -> None:
        """Registra um tenant no catálogo."""
        self._tenants[tenant.tenant_id] = tenant
        print(f"[REGISTRY] Tenant registrado com sucesso: {tenant.name} ({tenant.tenant_id})")

    def get_tenant(self, tenant_id: str) -> Optional[BaseTenant]:
        """Busca um tenant pelo seu identificador com tratamento defensivo."""
        try:
            tenant = self._tenants.get(tenant_id)
            if not tenant:
                raise ValueError(f"Tenant '{tenant_id}' não encontrado no sistema.")
        except Exception as error:
            print(f"[AVISO REGISTRY] {error}")
            return None
        else:
            return tenant

# Instância global leve
tenant_registry = TenantRegistry()