import openrouteservice
from openrouteservice.directions import directions

coords = ((8.34234,48.23424),(8.34423,48.26424))

client = openrouteservice.Client(key='cd0b0469530b4824f56946c4bb1d60279bc826005be0e25266b76eb3e55440ee')
routes = directions(client,coords)

print(routes)