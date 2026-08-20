"""Azure Data Lake writer for raw ingestion data."""

from __future__ import annotations

from typing import Any

from packages.signalwatch_common.azure_clients import create_data_lake_service_client


class AzureDataLakeRawWriter:
    """Persist raw file content to Azure Data Lake Storage Gen2."""

    def __init__(
        self,
        account_name: str,
        container_name: str,
        service_client: Any | None = None,
    ) -> None:
        if not account_name:
            raise ValueError("AZURE_STORAGE_ACCOUNT_NAME is required for Azure storage")
        if not container_name:
            raise ValueError("AZURE_STORAGE_CONTAINER_NAME is required for Azure storage")
        self.account_name = account_name
        self.container_name = container_name
        self.service_client = service_client or create_data_lake_service_client(account_name)

    def write(self, content: bytes, destination_path: str) -> str:
        """Upload bytes to ADLS and return an abfss URI."""
        normalized_path = destination_path.replace("\\", "/").lstrip("/")
        file_system_client = self.service_client.get_file_system_client(self.container_name)
        file_client = file_system_client.get_file_client(normalized_path)
        file_client.upload_data(content, overwrite=True)
        return (
            f"abfss://{self.container_name}@{self.account_name}.dfs.core.windows.net/"
            f"{normalized_path}"
        )
