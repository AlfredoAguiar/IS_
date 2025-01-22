import { NextRequest, NextResponse } from 'next/server';

export async function PUT(req: NextRequest) {
    const request_body = await req.json();
    const id = req.nextUrl.pathname.split("/")[3];

    // Validate required fields
    if (!id || !request_body.latitude || !request_body.longitude) {
        return NextResponse.json(
            { status: 400, message: "Missing required fields: id, latitude, or longitude." },

        );
    }

    const requestBody = {
        id,
        latitude: request_body.latitude,
        longitude: request_body.longitude,
        name: request_body.name || "Unknown",
    };

    const headers = {
        'Content-Type': 'application/json',
    };

    const options = {
        method: 'PUT',
        headers,
        body: JSON.stringify(requestBody),
    };

    try {
        // Perform the API call
        const response = await fetch(`${process.env.REST_API_BASE_URL}/api/cars/get-car-by-vinL/`, options);

        // Check if the response is not OK
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API error: ${errorText}`);
            return NextResponse.json(
                { status: response.status, message: response.statusText },

            );
        }

        // Parse the JSON response
        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Fetch error:", error);
        return NextResponse.json(
            { status: 500, message: "Internal Server Error", error: error.message },

        );
    }
}



