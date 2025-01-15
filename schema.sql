CREATE TABLE Cars (
    VIN VARCHAR(17) PRIMARY KEY,
    Condition INT,
    Odometer INT,
    Color VARCHAR(50),
    Interior VARCHAR(50),
    MMR INT
);

CREATE TABLE Specifications (
    SpecID INT AUTO_INCREMENT PRIMARY KEY,
    VIN VARCHAR(17),
    Year INT,
    Make VARCHAR(50),
    Model VARCHAR(50),
    Trim VARCHAR(50),
    Body VARCHAR(50),
    Transmission VARCHAR(50),
    FOREIGN KEY (VIN) REFERENCES Cars(VIN)
);

CREATE TABLE Sellers (
    SellerID INT AUTO_INCREMENT PRIMARY KEY,
    VIN VARCHAR(17),
    Name VARCHAR(255),
    State VARCHAR(10),
    SaleDate VARCHAR(255),
    SellingPrice INT,
    FOREIGN KEY (VIN) REFERENCES Cars(VIN)
);

CREATE TABLE Locations (
    LocationID INT AUTO_INCREMENT PRIMARY KEY,
    VIN VARCHAR(17),
    City VARCHAR(100),
    Latitude DECIMAL(9, 7),
    Longitude DECIMAL(10, 7),
    FOREIGN KEY (VIN) REFERENCES Cars(VIN)
);