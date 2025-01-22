import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    try {

        const { searchParams } = new URL(req.url);
        const vin = searchParams.get("vin");



        if (!vin) {
            return NextResponse.json(
                { error: "VIN is required" },

            );
        }


        const baseUrl = process.env.REST_API_BASE_URL;
        if (!baseUrl) {
            throw new Error('REST_API_BASE_URL environment variable is not set');
        }


        const url = `${baseUrl}/api/cars/get-car-by-vin/?vin=${vin}`;


        const response = await fetch(url, {
            method: "GET",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        });

        const responseData = await response.json();

        if (!response.ok) {
            return NextResponse.json(
                { error: responseData.error || response.statusText },

            );
        }


        return NextResponse.json({ cars: responseData });

    } catch (error: any) {

        return NextResponse.json(
            { error: error.message || "Internal Server Error" },

        );
    }
}