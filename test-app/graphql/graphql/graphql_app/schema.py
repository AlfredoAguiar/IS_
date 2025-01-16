import graphene

# Importing the resolvers and schemas for cars, locations, sellers, and specifications
from graphql_app.resolvers.Car import Query as CarQuery, Mutation as CarMutation
from graphql_app.resolvers.Location import Query as LocationQuery, UpdateLocation as LocationMutation
from graphql_app.resolvers.Seller import Query as SellerQuery, Mutation as SellerMutation
from graphql_app.resolvers.Specification import Query as SpecificationQuery, Mutation as SpecificationMutation

# Combine all queries
class Query(
    CarQuery,
    LocationQuery,
    SellerQuery,
    SpecificationQuery,
    graphene.ObjectType
):
    pass

# Combine all mutations
class Mutation(
    CarMutation,
    SellerMutation,
    SpecificationMutation,
    graphene.ObjectType
):
    update_location = LocationMutation.Field()  # Correctly assigning the mutation for updating location

# Define the complete GraphQL schema
schema = graphene.Schema(query=Query, mutation=Mutation)
