"use client"

import { useEffect, useRef, useState } from "react"
import type { FloorPlanData } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { ZoomIn, ZoomOut, Maximize, FileCode } from "lucide-react"

interface FloorPlanViewerProps {
  floorPlanData: FloorPlanData | null
}

export default function FloorPlanViewer({ floorPlanData }: FloorPlanViewerProps) {
  const [scale, setScale] = useState<number>(0.694444)
  const [autoScale, setAutoScale] = useState<number>(1)
  const [timestamp, setTimestamp] = useState<number>(Date.now())
  const [showXml, setShowXml] = useState<boolean>(false)
  const [svgContent, setSvgContent] = useState<string>("")
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (floorPlanData) {
      setTimestamp(Date.now())
    }
  }, [floorPlanData])

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

  // Helper: adaugă padding la viewBox-ul SVG-ului
  function addPaddingToSvg(svg: string, paddingPercent: number = 0.05): string {
    const viewBoxMatch = svg.match(/viewBox="([\d\.\- ]+)"/);
    if (!viewBoxMatch) return svg;
    const [minX, minY, width, height] = viewBoxMatch[1].split(" ").map(Number);
    const padX = width * paddingPercent;
    const padY = height * paddingPercent;
    const newViewBox = `${minX - padX} ${minY - padY} ${width + 2 * padX} ${height + 2 * padY}`;
    return svg.replace(/viewBox="[\d\.\- ]+"/, `viewBox="${newViewBox}"`);
  }

  // Auto-fit zoom logic
  useEffect(() => {
    if (!svgContent || !containerRef.current) return;
    // Extrage viewBox-ul
    const viewBoxMatch = svgContent.match(/viewBox="([\d\.\- ]+)"/);
    if (!viewBoxMatch) return;
    const [minX, minY, width, height] = viewBoxMatch[1].split(" ").map(Number);
    const container = containerRef.current;
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    // Calculează scale-ul pentru fit cu padding 5%
    const scaleX = containerWidth / (width * 1.1); // 10% extra pentru padding vizual
    const scaleY = containerHeight / (height * 1.1);
    const fitScale = Math.min(scaleX, scaleY, 1); // nu da zoom in peste 1
    setScale(fitScale);
    setAutoScale(fitScale);
  }, [svgContent, floorPlanData]);

  const handleZoomIn = () => {
    setScale((prev) => prev * 1.2)
  }

  const handleZoomOut = () => {
    setScale((prev) => prev / 1.2)
  }

  const handleResetZoom = () => {
    setScale(autoScale)
  }

  const toggleView = () => {
    setShowXml(!showXml)
  }

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
    <div className="relative h-full" ref={containerRef}>
      {!floorPlanData ? (
        <div className="flex flex-col items-center justify-center h-[500px] bg-white rounded-md border border-dashed border-gray-300">
          <div className="mb-2 text-gray-400">
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
          <p className="text-center text-gray-500">Parse your DSL code to see the floor plan</p>
          <p className="mt-1 text-sm text-center text-gray-400">
            Click the "Parse & Render" button to visualize your design
          </p>
        </div>
      ) : (
        <div className="overflow-auto border rounded-md bg-white h-[500px]">
          <div className="absolute z-10 flex gap-1 top-2 right-2">
            <Button variant="outline" size="icon" onClick={toggleView} className="w-8 h-8 bg-white">
              <FileCode className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleZoomIn} className="w-8 h-8 bg-white">
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleZoomOut} className="w-8 h-8 bg-white">
              <ZoomOut className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleResetZoom} className="w-8 h-8 bg-white">
              <Maximize className="w-4 h-4" />
            </Button>
          </div>
          <div className="min-h-full overflow-auto">
            {showXml ? (
              <pre className="p-4 overflow-auto font-mono text-xs whitespace-pre">{generateDslCode(floorPlanData)}</pre>
            ) : (
              svgContent && (
                <div style={{ transform: `scale(${scale})`, transformOrigin: "top left", transition: "transform 0.2s" }}>
                  <div dangerouslySetInnerHTML={{ __html: addPaddingToSvg(svgContent, 0.05) }} />
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  )
}