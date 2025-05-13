"use client"

import { useEffect, useRef, useState } from "react"
import type { FloorPlanData } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { ZoomIn, ZoomOut, Maximize, FileCode } from "lucide-react"

interface FloorPlanViewerProps {
  floorPlanData: FloorPlanData | null
}

export default function FloorPlanViewer({ floorPlanData }: FloorPlanViewerProps) {
  const [scale, setScale] = useState<number>(1) // Scale factor for SVG
  const [timestamp, setTimestamp] = useState<number>(Date.now()) // Added for cache busting
  const [showXml, setShowXml] = useState<boolean>(false) // Toggle for XML view
  const [svgContent, setSvgContent] = useState<string>("")

  // Update timestamp when floorPlanData changes
  useEffect(() => {
    if (floorPlanData) {
      setTimestamp(Date.now())
    }
  }, [floorPlanData])

  // Fetch SVG content when URL or timestamp changes
  useEffect(() => {
    if (!showXml && floorPlanData?.svg_url) {
      fetch(`http://localhost:5001${floorPlanData.svg_url}?t=${timestamp}`)
        .then(response => response.text())
        .then(text => {
          setSvgContent(text)
        })
        .catch(error => console.error("Error fetching SVG:", error))
    }
  }, [floorPlanData?.svg_url, timestamp, showXml])

  const handleZoomIn = () => {
    setScale((prev) => prev * 1.2)
  }

  const handleZoomOut = () => {
    setScale((prev) => prev / 1.2)
  }

  const handleResetZoom = () => {
    setScale(1)
  }

  const toggleView = () => {
    setShowXml(!showXml)
  }

  // Function to generate DSL code from FloorPlanData
  const generateDslCode = (data: FloorPlanData): string => {
    if (!data || !data.elements || data.elements.length === 0) return ""

    let code = "# size: 1000 x 1000\n\n"

    data.elements.forEach(element => {
      switch (element.type) {
        case "room":
          code += `Room {\n`
          code += `    id: "${element.id}";\n`
          if (element.label) code += `    label: "${element.label}";\n`
          if (element.position && element.size) {
            code += `    size: [${element.size[0]}, ${element.size[1]}];\n`
            code += `    position: [${element.position[0]}, ${element.position[1]}];\n`
          }
          code += `}\n\n`
          break
        case "wall":
          code += `Wall {\n`
          code += `    id: "${element.id}";\n`
          if (element.start && element.end) {
            code += `    start: [${element.start[0]}, ${element.start[1]}];\n`
            code += `    end: [${element.end[0]}, ${element.end[1]}];\n`
          }
          code += `}\n\n`
          break
        case "door":
          code += `Door {\n`
          code += `    id: "${element.id}";\n`
          if (element.position) {
            code += `    position: [${element.position[0]}, ${element.position[1]}];\n`
          }
          if (element.width) code += `    width: ${element.width};\n`
          if (element.height) code += `    height: ${element.height};\n`
          if (element.direction) code += `    direction: "${element.direction}";\n`
          code += `}\n\n`
          break
        case "window":
          code += `Window {\n`
          code += `    id: "${element.id}";\n`
          if (element.position) {
            code += `    position: [${element.position[0]}, ${element.position[1]}];\n`
          }
          if (element.width) code += `    width: ${element.width};\n`
          if (element.height) code += `    height: ${element.height};\n`
          code += `}\n\n`
          break
        case "bed":
        case "table":
        case "chair":
        case "stairs":
        case "elevator":
          const typeName = element.type.charAt(0).toUpperCase() + element.type.slice(1)
          code += `${typeName} {\n`
          code += `    id: "${element.id}";\n`
          if (element.position) {
            code += `    position: [${element.position[0]}, ${element.position[1]}];\n`
          }
          if (element.width) code += `    width: ${element.width};\n`
          if (element.height) code += `    height: ${element.height};\n`
          code += `}\n\n`
          break
      }
    })

    return code
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
            <Button variant="outline" size="icon" onClick={toggleView} className="h-8 w-8 bg-white">
              <FileCode className="h-4 w-4" />
            </Button>
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
            {showXml ? (
              <pre className="text-xs p-4 font-mono overflow-auto whitespace-pre">{generateDslCode(floorPlanData)}</pre>
            ) : (
              svgContent && (
                <div style={{ transform: `scale(${scale})`, transformOrigin: "top left", transition: "transform 0.2s" }}>
                  <div dangerouslySetInnerHTML={{ __html: svgContent }} />
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  )
}