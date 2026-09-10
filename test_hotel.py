from app.services.hotel_service import HotelService

service = HotelService()

result = service.get_hotels("Chennai")

print(result)