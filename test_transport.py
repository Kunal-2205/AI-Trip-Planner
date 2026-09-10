from app.services.transport_service import TransportService

service = TransportService()

result = service.compare_transport(
    source="Mumbai",
    destination="Chennai",
    budget=30000,
    travellers=2,
    preferred_transport="Any"
)

print(result.model_dump())