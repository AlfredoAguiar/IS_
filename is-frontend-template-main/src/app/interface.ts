export interface Car {
  vin: string;
  condition: number;
  odometer: number;
  mmr: number;
  specifications: {
    year: number;
    make: string;
    model: string;
    trim: string;
    body: string;
    transmission: string;
    color: string;
    interior: string;
  };
  seller_name: string;
  seller_state: string;
  seller_coordinates: {
    latitude: number;
    longitude: number;
  };
  sale_date: string;
  selling_price: number;
}

export interface Cars{
    cars: Car[]
}
export interface Car_{
    vin: number
    latitude: number
    longitude: number
}

export interface Cars_{
    cars_: Car_[]
}
export interface R_Cars{
    data: Cars_
}


export interface City{
    nome: string
    latitude: number
    longitude: number
    id: string
}

export interface Cities{
    cities: City[]
}

export interface GraphQlCities{
    data: Cities
}