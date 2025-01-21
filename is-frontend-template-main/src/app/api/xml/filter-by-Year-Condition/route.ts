import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    try {
        // Extract query parameters from the URL
        const { searchParams } = new URL(req.url);
        const year = searchParams.get("year");
        const condition = searchParams.get("condition");

        // Validate that both year and condition are provided
        if (!year || !condition) {
            return NextResponse.json(
                { error: "Year and condition are required" },

            );
        }

        // Convert year and condition to numbers
        const yearNumber = parseInt(year);
        const conditionNumber = parseInt(condition);

        // Validate if the values are valid numbers
        if (isNaN(yearNumber) || isNaN(conditionNumber)) {
            return NextResponse.json(
                { error: "'year' and 'condition' must be valid numbers" },

            );
        }

        // Get the base URL from environment variables
        const baseUrl = process.env.REST_API_BASE_URL;
        if (!baseUrl) {
            throw new Error('REST_API_BASE_URL environment variable is not set');
        }

        // Construct the URL for the external API call
        const url = `${baseUrl}/api/cars/year-condition/?year=${yearNumber}&condition=${conditionNumber}`;

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


