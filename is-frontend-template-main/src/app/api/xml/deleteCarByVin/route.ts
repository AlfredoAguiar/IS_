import { NextRequest, NextResponse } from 'next/server';

export async function DELETE(req: NextRequest) {
  try {
    // Extract VIN from the query parameters
    const url = new URL(req.url);
    const vin = url.searchParams.get('vin');

    if (!vin) {
      return NextResponse.json(
        { error: 'VIN is required' },

      );
    }

    // Validate VIN length (17 characters)
    if (vin.length !== 17) {
      return NextResponse.json(
        { error: 'VIN must be a 17-character string.' },

      );
    }

    // Send the DELETE request to your API
    const response = await fetch(`${process.env.REST_API_BASE_URL}/api/cars/delete-car/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ vin }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { success: true, vin },

      );
    }

    const result = await response.json();
    console.log('Delete response:', result);

    // If deletion was successful
    if (result.success) {
      return NextResponse.json(
        { success: true, vin },

      );
    } else {
      return NextResponse.json(
        { success: true, vin },

      );
    }
  } catch (error) {
    console.error('Error deleting car:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },

    );
  }
}