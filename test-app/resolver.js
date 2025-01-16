const db = require('./db');

const Query = {
  // Basic test and greeting queries
  test: () => 'Test Success',
  sayHello: (root, args) => `Hello ${args.name}, GraphQL server says Hello to you`,
  greeting: () => 'Hello! This is the GraphQL API for the Cars system!',

  // Query all cars
  cars: () => db.cars.list(),

  // Query a single car by VIN
  car: (root, args) => {
    return db.cars.get(args.VIN);
  },

  // Query all specifications
  specifications: () => db.specifications.list(),

  // Query a single specification by SpecID
  specification: (root, args) => {
    return db.specifications.get(args.SpecID);
  },

  // Query all sellers
  sellers: () => db.sellers.list(),

  // Query a single seller by SellerID
  seller: (root, args) => {
    return db.sellers.get(args.SellerID);
  },

  // Query all locations
  locations: () => db.locations.list(),

  // Query a single location by LocationID
  location: (root, args) => {
    return db.locations.get(args.LocationID);
  }
};

const Car = {
  specifications: (root) => {
    return db.specifications.list().filter(spec => spec.VIN === root.VIN);
  },
  sellers: (root) => {
    return db.sellers.list().filter(seller => seller.VIN === root.VIN);
  },
  locations: (root) => {
    return db.locations.list().filter(location => location.VIN === root.VIN);
  }
};

const Specification = {
  car: (root) => {
    return db.cars.get(root.VIN);
  }
};

const Seller = {
  car: (root) => {
    return db.cars.get(root.VIN);
  }
};

const Location = {
  car: (root) => {
    return db.cars.get(root.VIN);
  }
};

const Mutation = {
  // Create a new car
  addCar: (root, args) => {
    return db.cars.create({
      VIN: args.VIN,
      Condition: args.Condition,
      Odometer: args.Odometer,
      Color: args.Color,
      Interior: args.Interior,
      MMR: args.MMR
    });
  },

  // Create a new specification
  addSpecification: (root, args) => {
    return db.specifications.create({
      VIN: args.VIN,
      Year: args.Year,
      Make: args.Make,
      Model: args.Model,
      Trim: args.Trim,
      Body: args.Body,
      Transmission: args.Transmission
    });
  },

  // Create a new seller
  addSeller: (root, args) => {
    return db.sellers.create({
      VIN: args.VIN,
      Name: args.Name,
      State: args.State,
      SaleDate: args.SaleDate,
      SellingPrice: args.SellingPrice
    });
  },

  // Create a new location
  addLocation: (root, args) => {
    return db.locations.create({
      VIN: args.VIN,
      City: args.City,
      Latitude: args.Latitude,
      Longitude: args.Longitude
    });
  }
};

module.exports = { Query, Car, Specification, Seller, Location, Mutation };
