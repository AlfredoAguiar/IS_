import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const make = searchParams.get("make");
        const model = searchParams.get("model");

        if (!make || !model) {
            return NextResponse.json(
                { error: "Make and model are required" },

            );
        }

        const baseUrl = process.env.REST_API_BASE_URL;
        if (!baseUrl) {
            throw new Error('REST_API_BASE_URL environment variable is not set');
        }

        const url = `${baseUrl}/api/cars/make-model/?make=${make}&model=${model}`;

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