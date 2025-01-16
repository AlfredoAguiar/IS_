CREATE TABLE IF NOT EXISTS WeatherReports (
    ReportID SERIAL PRIMARY KEY,
    Region VARCHAR(100),
    Country VARCHAR(100),
    State VARCHAR(100),
    City VARCHAR(100),
    Date DATE,
    AvgTemperature DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS Coordinates (
    CoordinateID SERIAL PRIMARY KEY,
    ReportID INT,
    Latitude DECIMAL(9, 7),
    Longitude DECIMAL(10, 7),
    UNIQUE (ReportID),
    FOREIGN KEY (ReportID) REFERENCES WeatherReports(ReportID)
);
