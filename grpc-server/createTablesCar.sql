
CREATE TABLE IF NOT EXISTS Cars (
                        VIN VARCHAR(17) PRIMARY KEY,
                        Condition INT,
                        Odometer INT,
                        Color VARCHAR(50),
                        Interior VARCHAR(50),
                        MMR INT
                    );

                    CREATE TABLE IF NOT EXISTS Specifications (
                        SpecID SERIAL PRIMARY KEY,
                        VIN VARCHAR(17),
                        Year INT,
                        Make VARCHAR(50),
                        Model VARCHAR(50),
                        Trim VARCHAR(50),
                        Body VARCHAR(50),
                        Transmission VARCHAR(50),
                        UNIQUE (VIN),
                        FOREIGN KEY (VIN) REFERENCES Cars(VIN)
                    );

                    CREATE TABLE IF NOT EXISTS Sellers (
                        SellerID SERIAL PRIMARY KEY,
                        VIN VARCHAR(17),
                        Name VARCHAR(255),
                        State VARCHAR(10),
                        SaleDate VARCHAR(255),
                        SellingPrice INT,
                        UNIQUE (VIN),
                        FOREIGN KEY (VIN) REFERENCES Cars(VIN)
                    );

                    CREATE TABLE IF NOT EXISTS Locations (
                        LocationID SERIAL PRIMARY KEY,
                        VIN VARCHAR(17),
                        City VARCHAR(100),
                        Latitude DECIMAL(9, 7),
                        Longitude DECIMAL(10, 7),
                        UNIQUE (VIN),
                        FOREIGN KEY (VIN) REFERENCES Cars(VIN)
                    );
