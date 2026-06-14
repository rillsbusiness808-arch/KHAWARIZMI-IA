# tests/test_mindmap.py
# Tests du Mind Map JSON Dynamique (Pilier 4)

import pytest
from httpx import AsyncClient


VALID_REQUEST = {
    "matiere": "SVT",
    "chapitre": "Photosynthèse",
    "filiere": "Sciences Naturelles",
    "niveau_detail": "standard"
}


class TestMindMapAuth:
    async def test_generate_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/mindmap/generate",
            json=VALID_REQUEST
        )
        assert response.status_code in [401, 503]


class TestMindMapMaitrise:
    async def test_update_maitrise_invalid_value(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.patch(
            "/api/mindmap/fake-node/maitrise",
            headers=auth_headers,
            json={"maitrise": 5}
        )
        assert response.status_code in [400, 401, 422, 503]
