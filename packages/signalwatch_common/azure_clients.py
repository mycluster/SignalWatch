"""Azure SDK client factories."""

from __future__ import annotations

from typing import Any


def create_data_lake_service_client(account_name: str) -> Any:
    """Create an ADLS Gen2 service client using default Azure credentials."""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.storage.filedatalake import DataLakeServiceClient
    except ModuleNotFoundError as error:
        message = (
            "Azure storage support requires azure-identity and "
            "azure-storage-file-datalake to be installed."
        )
        raise RuntimeError(message) from error

    account_url = f"https://{account_name}.dfs.core.windows.net"
    return DataLakeServiceClient(
        account_url=account_url,
        credential=DefaultAzureCredential(),
    )
