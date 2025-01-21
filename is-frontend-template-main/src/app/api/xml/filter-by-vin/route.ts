import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    try {
        // Extract query parameters from the URL
        const { searchParams } = new URL(req.url);
        const vin = searchParams.get("vin");



        if (!vin) {
            return NextResponse.json(
                { error: "VIN is required" },

            );
        }


        // Get the base URL from environment variables
        const baseUrl = process.env.REST_API_BASE_URL;
        if (!baseUrl) {
            throw new Error('REST_API_BASE_URL environment variable is not set');
        }

        // Construct the URL for the external API call
        const url = `${baseUrl}/api/cars/get-car-by-vin/?vin=${vin}`;

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