Drop table Specifications;
Drop table Sellers;
Drop table Locations;


CREATE TABLE IF NOT EXISTS Cars (
    VIN VARCHAR(17) PRIMARY KEY,
    Condition INT,
    Odometer INT,
    Color VARCHAR(50) DEFAULT '',
    Interior VARCHAR(50) DEFAULT '',
    MMR INT
);


CREATE TABLE IF NOT EXISTS Specifications (
    SpecID SERIAL PRIMARY KEY,
    VIN VARCHAR(17) UNIQUE,
    Year INT,
    Make VARCHAR(50),
    Model VARCHAR(50),
    Trim VARCHAR(50),
    Body VARCHAR(50),
    Transmission VARCHAR(50),
    FOREIGN KEY (VIN) REFERENCES Cars(VIN) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Sellers (
    SellerID SERIAL PRIMARY KEY,
    VIN VARCHAR(17) UNIQUE,
    Name VARCHAR(255),
    State VARCHAR(10),
    SaleDate VARCHAR(255),
    SellingPrice INT,
    FOREIGN KEY (VIN) REFERENCES Cars(VIN) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Locations (
    LocationID SERIAL PRIMARY KEY,
    VIN VARCHAR(17) UNIQUE,
    City VARCHAR(100),
    Latitude DECIMAL(9, 7),
    Longitude DECIMAL(10, 7),
    FOREIGN KEY (VIN) REFERENCES Cars(VIN) ON DELETE CASCADE
);

