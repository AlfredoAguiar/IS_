import graphene
from db.connection import execute_query  # Assuming this is the function to run SQL queries

class SpecificationType(graphene.ObjectType):
    VIN = graphene.String()
    Year = graphene.String()
    Make = graphene.String()
    Model = graphene.String()
    Trim = graphene.String()
    Body = graphene.String()
    Transmission = graphene.String()


# Queries to list all entities (cars, specifications, sellers, locations)
class Query(graphene.ObjectType):
    specifications = graphene.List(SpecificationType)

    # Resolver for specifications
    def resolve_specifications(self, info):
        query = "SELECT VIN, Year, Make, Model, Trim, Body, Transmission FROM specifications"
        result = execute_query(query)
        return [SpecificationType(VIN=row[0], Year=row[1], Make=row[2], Model=row[3], Trim=row[4], Body=row[5], Transmission=row[6]) for row in result]

# Mutation to create a new specification
class CreateSpecification(graphene.Mutation):
    class Arguments:
        VIN = graphene.String(required=True)
        Year = graphene.String(required=True)
        Make = graphene.String(required=True)
        Model = graphene.String(required=True)
        Trim = graphene.String(required=True)
        Body = graphene.String(required=True)
        Transmission = graphene.String(required=True)

    specification = graphene.Field(lambda: SpecificationType)

    def mutate(self, info, VIN, Year, Make, Model, Trim, Body, Transmission):
        query = """
            INSERT INTO specifications (VIN, Year, Make, Model, Trim, Body, Transmission)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING VIN, Year, Make, Model, Trim, Body, Transmission
        """
        result = execute_query(query, (VIN, Year, Make, Model, Trim, Body, Transmission))
        return CreateSpecification(specification=SpecificationType(VIN=result[0][0], Year=result[0][1], Make=result[0][2], Model=result[0][3], Trim=result[0][4], Body=result[0][5], Transmission=result[0][6]))



# Add mutations to the schema
class Mutation(graphene.ObjectType):
    create_specification = CreateSpecification.Field()
