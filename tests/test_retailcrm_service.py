from typing import Any, Iterable
import sys
import importlib
import pytest


def _ensure_fresh_imports(names: Iterable[str]) -> None:
    """Remove named modules from sys.modules to force fresh imports."""
    for m in list(sys.modules):
        for name in names:
            if m.startswith(name):
                sys.modules.pop(m, None)


def setup_retail_service() -> Any:
    """Prepare a RetailCRMService instance using values from `env.test`."""

    _ensure_fresh_imports(
        [
            "src.core.config",
            "src.services.integrations.retail_crm.constants",
            "src.services.integrations.retail_crm.api_service",
        ]
    )

    mod = importlib.import_module("src.services.integrations.retail_crm.api_service")
    RetailCRMService = mod.RetailCRMService
    svc = RetailCRMService()
    return svc


@pytest.mark.asyncio
async def test_prepare_params_and_headers() -> None:
    """Verify that request params include API key and headers are set per method."""
    svc = setup_retail_service()

    params = svc._prepare_request_params({"a": 1})
    assert params["a"] == 1
    assert params.get("apiKey") == "abc123"

    from src.services.integrations.constants_base import HTTPMethod

    headers_post = svc._prepare_request_headers(None, method=HTTPMethod.POST)
    assert headers_post.get("Content-Type") == "application/x-www-form-urlencoded"

    headers_get = svc._prepare_request_headers(None, method=HTTPMethod.GET)
    assert headers_get.get("Content-Type") is None

    await svc.close()


@pytest.mark.asyncio
async def test_convert_filters_flat_and_nested() -> None:
    """Ensure filters are converted into RetailCRM-style query parameters."""
    svc = setup_retail_service()

    from src.schemas.customers import CustomerFiltersSchema

    fs = CustomerFiltersSchema(name="John", limit=10, page=2)
    params = svc._convert_filter_data_to_retail_crm_style(fs)
    assert params["limit"] == 10
    assert params["page"] == 2
    assert params.get("filter[name]") == "John"

    # nested/list case: list of dicts becomes keys like 'filter[phones][][number]'
    data = {
        "limit": 5,
        "page": 1,
        "phones": [{"number": "1"}, {"number": "2"}],
        "name": "X",
    }
    params2 = svc._convert_filter_data_to_retail_crm_style(data)

    # keys for phones should start with 'filter[phones]'
    assert any(k.startswith("filter[phones]") for k in params2.keys())

    # at least one phone value should be present
    phone_vals = [v for k, v in params2.items() if k.startswith("filter[phones]")]
    assert any(v in ("1", "2") for v in phone_vals)

    await svc.close()
