import graphene
from db.connection import execute_query  # Assuming this is the function to run SQL queries

class LocationType(graphene.ObjectType):
    VIN = graphene.String()
    City = graphene.String()
    Latitude = graphene.Float()
    Longitude = graphene.Float()

# Queries to list all entities (locations)
class Query(graphene.ObjectType):
    locations = graphene.List(LocationType)

    # Resolver for locations
    def resolve_locations(self, info):
        query = "SELECT VIN, City, Latitude, Longitude FROM locations"
        result = execute_query(query)
        return [
            LocationType(
                VIN=row[0], 
                City=row[1], 
                Latitude=row[2], 
                Longitude=row[3]
            ) 
            for row in result
        ]

# Mutation to create a new location
class CreateLocation(graphene.Mutation):
    class Arguments:
        VIN = graphene.String(required=True)
        City = graphene.String(required=True)
        Latitude = graphene.Float(required=True)
        Longitude = graphene.Float(required=True)

    location = graphene.Field(lambda: LocationType)

    def mutate(self, info, VIN, City, Latitude, Longitude):
        query = """
            INSERT INTO locations (VIN, City, Latitude, Longitude)
            VALUES (%s, %s, %s, %s)
            RETURNING VIN, City, Latitude, Longitude
        """
        result = execute_query(query, (VIN, City, Latitude, Longitude))
        return CreateLocation(
            location=LocationType(
                VIN=result[0][0], 
                City=result[0][1], 
                Latitude=result[0][2], 
                Longitude=result[0][3]
            )
        )

# Mutation to update an existing location
class UpdateLocation(graphene.Mutation):
    class Arguments:
        VIN = graphene.String(required=True)
        Latitude = graphene.Float(required=True)
        Longitude = graphene.Float(required=True)

    location = graphene.Field(lambda: LocationType)

    def mutate(self, info, VIN, Latitude, Longitude):
        # Validate latitude and longitude ranges
        if Latitude < -90 or Latitude > 90:
            raise ValueError('Invalid latitude value. It must be between -90 and 90.')
        if Longitude < -180 or Longitude > 180:
            raise ValueError('Invalid longitude value. It must be between -180 and 180.')

        update_query = """
            UPDATE locations SET Latitude = %s, Longitude = %s
            WHERE VIN = %s
            RETURNING VIN, City, Latitude, Longitude
        """
        result = execute_query(update_query, (Latitude, Longitude, VIN))

        if not result:
            raise Exception('Location not found for the provided VIN.')

        return UpdateLocation(
            location=LocationType(
                VIN=result[0][0], 
                City=result[0][1], 
                Latitude=result[0][2], 
                Longitude=result[0][3]
            )
        )

# Combine all mutations for locations
class Mutation(graphene.ObjectType):
    update_location = UpdateLocation.Field()
