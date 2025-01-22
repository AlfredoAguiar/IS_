import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const formData = await req.formData();
    const body = Object.fromEntries(formData);
    const file = (body.file as Blob) || null;

    if (!file) {
        return NextResponse.json({ status: 500, message: 'Files not sent!' }, );
    }

    const formdata = new FormData();
    formdata.append("file", file);

    const requestOptions = {
        method: "POST",
        body: formdata
    };

    try {

        const uploadResponse = await fetch(`${process.env.REST_API_BASE_URL}/api/upload-file/by-chunks`, requestOptions);
    
        if (!uploadResponse.ok) {
            return NextResponse.json({ status: uploadResponse.status, message: uploadResponse.statusText }, );
        }
    
        // Check if the response is JSON
        const contentType = uploadResponse.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            return NextResponse.json({ status: 500, message: "Invalid response format from server" }, );
        }
    
        // Parse the response JSON safely
        const responseData = await uploadResponse.json();
        return NextResponse.json(responseData);
    
    } catch (e) {
        console.error("Error:", e); // Log the error for debugging
        return NextResponse.json({ status: 500, message: "Internal server error" }, { status: 500 });
    }
}