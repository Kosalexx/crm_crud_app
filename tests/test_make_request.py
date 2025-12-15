from typing import Any
import importlib
import sys
import pytest
import respx


def setup_service_for_request() -> Any:
    """Create a RetailCRMService instance using values from `env.test`."""

    for mod in list(sys.modules):
        if mod.startswith("src.services.integrations.retail_crm.api_service") or mod.startswith("src.core.config"):
            sys.modules.pop(mod, None)

    module = importlib.import_module("src.services.integrations.retail_crm.api_service")
    return module.RetailCRMService()


@pytest.mark.asyncio
@respx.mock
async def test_make_request_success(respx_mock: respx.MockRouter) -> None:
    """_make_request should return parsed JSON for a successful response."""
    svc = setup_service_for_request()

    expected_url = f"{svc.api_url}/customers"
    respx_mock.get(expected_url).respond(200, json={"success": True, "customers": []})

    result = await svc._make_request("GET", "/customers", params={})
    assert isinstance(result, dict)
    assert result.get("success") is True

    await svc.close()


@pytest.mark.asyncio
@respx.mock
async def test_make_request_http_status_error(respx_mock: respx.MockRouter) -> None:
    """_make_request should raise a CRM API error on HTTP status failures."""
    svc = setup_service_for_request()

    expected_url = f"{svc.api_url}/customers"
    respx_mock.get(expected_url).respond(500, text="internal")

    with pytest.raises(Exception) as exc:
        await svc._make_request("GET", "/customers")

    # error message should mention HTTP status
    assert "CRM API error" in str(exc.value)
    assert "HTTP 500" in str(exc.value)

    await svc.close()


@pytest.mark.asyncio
@respx.mock
async def test_make_request_invalid_response_validation(
    respx_mock: respx.MockRouter,
) -> None:
    """If the CRM returns a success=False payload, validation should cause a Request error."""
    svc = setup_service_for_request()

    expected_url = f"{svc.api_url}/customers"
    respx_mock.get(expected_url).respond(200, json={"success": False, "errorMsg": "bad"})

    with pytest.raises(Exception) as exc:
        await svc._make_request("GET", "/customers")

    assert "Request error" in str(exc.value)
    assert "RetailCRM API error" in str(exc.value)

    await svc.close()
