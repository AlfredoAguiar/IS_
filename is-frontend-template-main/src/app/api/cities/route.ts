import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const request_body  = await req.json()

    const city          = request_body?.search ?? ''

    return NextResponse.json({
        "data": {
            "cities": [
                {
                    "nome": "Abadia de Goiás",
                    "latitude": -16.7573,
                    "longitude": -49.4412,
                    "id": "645755"
                },
                {
                    "nome": "Abadia dos Dourados",
                    "latitude": -18.4831,
                    "longitude": -47.3916,
                    "id": "645756"
                },
                {
                    "nome": "Sítio d'Abadia",
                    "latitude": -14.7992,
                    "longitude": -46.2506,
                    "id": "650821"
                }
            ]
        }
    }) 

    const headers = {
        'content-type': 'application/json',
    }
    
    const requestBody = {
        query: `query Cities {
            cities${city.length > 0 ? `(nome: "${city}")` : ``} {
                nome
                latitude
                longitude
                id
            }
        }`
    }
    
    const options = {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
    }

    try{
        const promise = await fetch(`${process.env.GRAPHQL_API_BASE_URL}/graphql/cities/`, options)

        if(!promise.ok){
            console.log(promise.statusText)
            return NextResponse.json({status: promise.status, message: promise.statusText}, { status: promise.status }) 
        }

        const data = await promise.json()

        return NextResponse.json(data) 
    }catch(e){
        console.log(e)
        return NextResponse.json({status: 500, message: e}, { status: 500  }) 
    }
}