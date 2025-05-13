import type { FloorPlanData } from "./types"

export async function parseFloorPlan(dslCode: string): Promise<FloorPlanData> {
  console.log("Sending DSL code to backend:", dslCode.substring(0, 100) + "...")

  try {
    if (!dslCode || dslCode.trim() === "") {
      throw new Error("No DSL code provided")
    }

    const response = await fetch("http://localhost:5001/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: dslCode }),
    })

    console.log("Response status:", response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error("API error:", errorText)
      throw new Error(`Failed to parse floor plan: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    console.log("Parsed data:", data)

    if (!data.elements || !Array.isArray(data.elements)) {
      throw new Error("Invalid response format from server")
    }

    return data
  } catch (error) {
    console.error("Error parsing floor plan:", error)
    throw error
  }
}