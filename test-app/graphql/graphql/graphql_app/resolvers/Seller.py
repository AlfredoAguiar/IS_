import graphene
from db.connection import execute_query  # Assuming this is the function to run SQL queries

# GraphQL Object Types
class SellerType(graphene.ObjectType):
    VIN = graphene.String()
    Name = graphene.String()
    State = graphene.String()
    SaleDate = graphene.String()
    SellingPrice = graphene.String()


# Queries to list all entities (cars, specifications, sellers, locations)
class Query(graphene.ObjectType):
    sellers = graphene.List(SellerType)

    # Resolver for sellers
    def resolve_sellers(self, info):
        query = "SELECT VIN, Name, State, SaleDate, SellingPrice FROM sellers"
        result = execute_query(query)
        return [SellerType(VIN=row[0], Name=row[1], State=row[2], SaleDate=row[3], SellingPrice=row[4]) for row in result]

# Mutation to create a new seller
class CreateSeller(graphene.Mutation):
    class Arguments:
        VIN = graphene.String(required=True)
        Name = graphene.String(required=True)
        State = graphene.String(required=True)
        SaleDate = graphene.String(required=True)
        SellingPrice = graphene.String(required=True)

    seller = graphene.Field(lambda: SellerType)

    def mutate(self, info, VIN, Name, State, SaleDate, SellingPrice):
        query = """
            INSERT INTO sellers (VIN, Name, State, SaleDate, SellingPrice)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING VIN, Name, State, SaleDate, SellingPrice
        """
        result = execute_query(query, (VIN, Name, State, SaleDate, SellingPrice))
        return CreateSeller(seller=SellerType(VIN=result[0][0], Name=result[0][1], State=result[0][2], SaleDate=result[0][3], SellingPrice=result[0][4]))

# Add mutations to the schema
class Mutation(graphene.ObjectType):
    create_seller = CreateSeller.Field()
