from app.services.geo_service import GeoService
from app.services.route_service import RouteService

geo = GeoService()
route = RouteService()

mumbai = geo.get_coordinates("Mumbai")
chennai = geo.get_coordinates("Chennai")

result = route.get_route(mumbai, chennai)

print(result)