import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { code } = await request.json()

    // const response = await fetch('http://your-flask-backend/parse', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ code })
    // });
    //
    // if (!response.ok) {
    //   throw new Error('Failed to parse floor plan');
    // }
    //
    // const data = await response.json();
    // return NextResponse.json(data);

    // For now, return a mock response
    return NextResponse.json({
      elements: [
        {
          id: "living_room",
          type: "room",
          position: [0, 0],
          size: [10, 8],
        },
        {
          id: "north_wall",
          type: "wall",
          start: [0, 0],
          end: [10, 0],
        },
        {
          id: "east_wall",
          type: "wall",
          start: [10, 0],
          end: [10, 8],
        },
        {
          id: "south_wall",
          type: "wall",
          start: [10, 8],
          end: [0, 8],
        },
        {
          id: "west_wall",
          type: "wall",
          start: [0, 8],
          end: [0, 0],
        },
      ],
    })
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 500 })
  }
}
