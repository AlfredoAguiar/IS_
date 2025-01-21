import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    try {
        // Extract query parameters from the URL
        const { searchParams } = new URL(req.url);
        const min_price = searchParams.get("min_price");
        const max_price = searchParams.get("max_price");

        // Check if both min_price and max_price are provided and can be parsed into numbers
        if (!min_price || !max_price) {
            return NextResponse.json(
                { error: "Both 'min_price' and 'max_price' are required" },

            );
        }

        // Convert the query parameters to numbers
        const minPriceNumber = parseFloat(min_price);
        const maxPriceNumber = parseFloat(max_price);

        // Check if the parsed numbers are valid
        if (isNaN(minPriceNumber) || isNaN(maxPriceNumber)) {
            return NextResponse.json(
                { error: "'min_price' and 'max_price' must be valid numbers" },

            );
        }

        // Get the base URL from environment variables
        const baseUrl = process.env.REST_API_BASE_URL;
        if (!baseUrl) {
            throw new Error('REST_API_BASE_URL environment variable is not set');
        }

        // Construct the URL for the external API call
        const url = `${baseUrl}/api/cars/price-range/?min_price=${minPriceNumber}&max_price=${maxPriceNumber}`;

        // Fetch data from the external API
        const response = await fetch(url, {
            method: "GET",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        });

        // Parse the JSON response from the external API
        const responseData = await response.json();

        // Check if the external API request was successful
        if (!response.ok) {
            return NextResponse.json(
                { error: responseData.error || response.statusText },

            );
        }

        // Return the response data as JSON
        return NextResponse.json({ cars: responseData });

    } catch (error: any) {
        // Handle unexpected errors
        return NextResponse.json(
            { error: error.message || "Internal Server Error" },

        );
    }
}