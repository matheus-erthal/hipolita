from typing import List, Optional
from ...types import Dataset, Resource
from ..interfaces.portal import Portal
from ..adapters.ckan_adapter import CkanAdapter

class PortalDataGovUS(Portal):
    """
    Implementação para catalog.data.gov (US)
    """
    
    def __init__(self, **config):
        super().__init__(**config)
        # URL base do catálogo CKAN dos EUA
        self.adapter = CkanAdapter("https://catalog.data.gov")

    async def search(self, query: str) -> List[Dataset]:
        results = []
        async with self.adapter as ad:
            # Data.gov as vezes tem redirects ou validações chatas, mas é CKAN standard
            if not await ad.connect():
                print("Não foi possível conectar ao data.gov")
                return []

            raw_packages = await ad.search_packages(query)
            
            for pkg in raw_packages:
                dataset = self._map_package_to_dataset(pkg)
                results.append(dataset)
        
        return results

    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        async with self.adapter as ad:
            raw_pkg = await ad.get_package(dataset_id)
            if raw_pkg:
                return self._map_package_to_dataset(raw_pkg)
        return None

    def _map_package_to_dataset(self, pkg: dict) -> Dataset:
        """
        Mapeia CKAN US -> Hipólita Dataset. 
        Similar ao BR, mas campos de metadados extra podem variar.
        """
        resources = []
        for res in pkg.get("resources", []):
            resources.append(Resource(
                id=res.get("id"),
                name=res.get("name"),
                description=res.get("description"),
                format=res.get("format"),
                url=res.get("url"),
                mimetype=res.get("mimetype"),
                created=res.get("created"),
                last_modified=res.get("last_modified"),
                size_bytes=res.get("size")
            ))
            
        tags = [t.get("name") for t in pkg.get("tags", [])]
        
        return Dataset(
            id=pkg.get("id"),
            title=pkg.get("title"),
            description=pkg.get("notes"),
            resources=resources,
            tags=tags,
            organization=pkg.get("organization", {}).get("title"),
            license=pkg.get("license_title"),
            source_portal="data.gov"
        )
