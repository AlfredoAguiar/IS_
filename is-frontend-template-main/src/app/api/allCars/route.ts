import { NextRequest, NextResponse } from "next/server";

interface City {
    nome: string;
    latitude: number;
    longitude: number;
    id: string;
}

let cachedCities: City[] = [];


async function fetchCityData() {
    try {
        const response = await fetch(`${process.env.REST_API_BASE_URL}/api/cars/all_L2/`);
        if (!response.ok) {
            throw new Error("Failed to fetch city data");
        }

        const data = await response.json();

        cachedCities = data?.cities ?? [];
        console.log("City data fetched:", cachedCities);
    } catch (error) {
        console.error("Error fetching city data:", error);
    }
}


fetchCityData();

export async function POST(req: NextRequest) {
    try {
        // Parse the request body
        const request_body = await req.json();
        console.log("Request body received:", request_body);

        const city = request_body?.search ?? '';
        console.log("Search term extracted:", city);

        // Check if cachedCities is populated
        if (!cachedCities || cachedCities.length === 0) {
            console.warn("Cached cities array is empty:", cachedCities);
        }

        // Filter cities based on search term
        const citiesToReturn = cachedCities.filter((cityItem) => {
            // Log each city being checked
            console.log("Checking city:", cityItem);

            // Defensive programming: Ensure `nome` is defined
            if (!cityItem.nome) {
                console.warn("City item missing 'nome':", cityItem);
                return false;
            }

            return cityItem.nome.toLowerCase().includes(city.toLowerCase());
        });

        console.log("Filtered cities:", citiesToReturn);

        // Return filtered cities
        return NextResponse.json({
            data: {
                cities: citiesToReturn,
            },
        });
    } catch (error) {
        // Log errors for debugging
        console.error("Error in POST request:", error);

        return NextResponse.json(
            { error: "An error occurred while processing the request." },
        );
    }
}