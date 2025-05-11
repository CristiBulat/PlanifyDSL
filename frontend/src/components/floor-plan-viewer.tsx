"use client"

import { useEffect, useRef, useState } from "react"
import type { FloorPlanData } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { ZoomIn, ZoomOut, Maximize } from "lucide-react"

interface FloorPlanViewerProps {
  floorPlanData: FloorPlanData | null
}

export default function FloorPlanViewer({ floorPlanData }: FloorPlanViewerProps) {
  const [scale, setScale] = useState<number>(1) // Scale factor for SVG
  const [timestamp, setTimestamp] = useState<number>(Date.now()); // Added for cache busting

  // Update timestamp when floorPlanData changes
  useEffect(() => {
    if (floorPlanData) {
      setTimestamp(Date.now());
    }
  }, [floorPlanData]);

  const handleZoomIn = () => {
    setScale((prev) => prev * 1.2)
  }

  const handleZoomOut = () => {
    setScale((prev) => prev / 1.2)
  }

  const handleResetZoom = () => {
    setScale(1)
  }

  return (
    <div className="relative h-full">
      {!floorPlanData ? (
        <div className="flex flex-col items-center justify-center h-[500px] bg-white rounded-md border border-dashed border-gray-300">
          <div className="text-gray-400 mb-2">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M3 7.8V3H7.8M16.2 3H21V7.8M21 16.2V21H16.2M7.8 21H3V16.2"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M7 12H17M12 7V17"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <p className="text-gray-500 text-center">Parse your DSL code to see the floor plan</p>
          <p className="text-gray-400 text-sm text-center mt-1">
            Click the "Parse & Render" button to visualize your design
          </p>
        </div>
      ) : (
        <div className="overflow-auto border rounded-md bg-white h-[500px]">
          <div className="absolute top-2 right-2 flex gap-1 z-10">
            <Button variant="outline" size="icon" onClick={handleZoomIn} className="h-8 w-8 bg-white">
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleZoomOut} className="h-8 w-8 bg-white">
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleResetZoom} className="h-8 w-8 bg-white">
              <Maximize className="h-4 w-4" />
            </Button>
          </div>
          <div className="min-h-full overflow-auto">
            {floorPlanData.svg_url && (
              <div style={{ transform: `scale(${scale})`, transformOrigin: "top left", transition: "transform 0.2s" }}>
                <img
                  src={`http://localhost:5001${floorPlanData.svg_url}?t=${timestamp}`}
                  alt="Floor Plan" 
                  className="min-w-full min-h-full"
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}