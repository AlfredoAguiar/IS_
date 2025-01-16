const { DataStore } = require('notarealdb');

// Create a DataStore instance pointing to the `data` directory
const store = new DataStore('./data');

module.exports = {
  cars: store.collection('cars'),
  specifications: store.collection('specifications'),
  sellers: store.collection('sellers'),
  locations: store.collection('locations'),
};
