import graphene
from db.connection import execute_query  # Assuming this is the function to run SQL queries

# GraphQL Object Types
class CarType(graphene.ObjectType):
    VIN = graphene.String()
    Condition = graphene.String()
    Odometer = graphene.String()
    Color = graphene.String()
    Interior = graphene.String()
    MMR = graphene.String()


# Queries to list all entities (cars, specifications, sellers, locations)
class Query(graphene.ObjectType):
    cars = graphene.List(CarType)

    # Resolver for cars
    def resolve_cars(self, info):
        query = "SELECT VIN, Condition, Odometer, Color, Interior, MMR FROM cars"
        result = execute_query(query)
        return [CarType(VIN=row[0], Condition=row[1], Odometer=row[2], Color=row[3], Interior=row[4], MMR=row[5]) for row in result]


# Mutation to create a new car
class CreateCar(graphene.Mutation):
    class Arguments:
        VIN = graphene.String(required=True)
        Condition = graphene.String(required=True)
        Odometer = graphene.String(required=True)
        Color = graphene.String(required=True)
        Interior = graphene.String(required=True)
        MMR = graphene.String(required=True)

    car = graphene.Field(lambda: CarType)

    def mutate(self, info, VIN, Condition, Odometer, Color, Interior, MMR):
        query = """
            INSERT INTO cars (VIN, Condition, Odometer, Color, Interior, MMR)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING VIN, Condition, Odometer, Color, Interior, MMR
        """
        result = execute_query(query, (VIN, Condition, Odometer, Color, Interior, MMR))
        return CreateCar(car=CarType(VIN=result[0][0], Condition=result[0][1], Odometer=result[0][2], Color=result[0][3], Interior=result[0][4], MMR=result[0][5]))


# Add mutations to the schema
class Mutation(graphene.ObjectType):
    create_car = CreateCar.Field()
