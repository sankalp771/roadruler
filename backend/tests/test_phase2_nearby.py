def test_nearby_endpoint_uses_postgis_meter_radius(auth_client):
    response = auth_client.get(
        "/api/v1/complaints/nearby",
        params={"latitude": 19.076, "longitude": 72.8777, "radius_meters": 50},
    )

    assert response.status_code == 200, response.text
    complaints = response.json()
    assert isinstance(complaints, list)
    assert all(item["distance_meters"] <= 50 for item in complaints)
    assert all("user_id" not in item for item in complaints)


def test_nearby_endpoint_rejects_invalid_coordinates(auth_client):
    response = auth_client.get(
        "/api/v1/complaints/nearby",
        params={"latitude": 91, "longitude": 72.8777},
    )

    assert response.status_code == 422
