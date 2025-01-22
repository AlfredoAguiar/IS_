import { NextRequest, NextResponse } from 'next/server';

export async function PUT(req: NextRequest) {
  try {
    // Parse JSON body from the request
    const requestBody = await req.json();
    const { vin, seller_name, seller_state, sale_date, selling_price } = requestBody;

    // Validate required parameters
    if (!vin) {
      return NextResponse.json({ error: 'VIN is required' });
    }
    if (vin.length !== 17) {
      return NextResponse.json({ error: 'VIN must be a 17-character string.' });
    }
    if (!seller_name) {
      return NextResponse.json({ error: 'Seller name is required' });
    }
    if (!seller_state) {
      return NextResponse.json({ error: 'Seller state is required' });
    }
    if (!sale_date) {
      return NextResponse.json({ error: 'Sale date is required' });
    }
    if (!selling_price) {
      return NextResponse.json({ error: 'Selling price is required' });
    }

    // Parse and validate selling price
    const parsedSellingPrice = parseFloat(selling_price);
    if (isNaN(parsedSellingPrice)) {
      return NextResponse.json({ error: 'Selling price must be a valid number.' });
    }

    // Construct the request body to update the car
    const updateCarBody = {
      vin,
      seller_name,
      seller_state,
      sale_date,
      selling_price: parsedSellingPrice,
    };

    // Send the PUT request to update the car in the external API
    const response = await fetch(`${process.env.REST_API_BASE_URL}/api/cars/update-car/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateCarBody),
    });

    // Handle the API response
    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json({
        error: errorData.error || 'Failed to update the car.',
      });
    }

    const result = await response.json();

    // Return success response
    return NextResponse.json({ success: true, result });
  } catch (error) {
    console.error('Error updating car:', error);
    return NextResponse.json({ error: 'Internal Server Error' });
  }
}