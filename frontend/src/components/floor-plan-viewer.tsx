"use client"

import { useEffect, useRef, useState } from "react"
import type { FloorPlanData, FloorPlanElement } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { ZoomIn, ZoomOut, Maximize } from "lucide-react"

interface FloorPlanViewerProps {
  floorPlanData: FloorPlanData | null
}

export default function FloorPlanViewer({ floorPlanData }: FloorPlanViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [scale, setScale] = useState<number>(40) // pixels per meter

  useEffect(() => {
    if (!floorPlanData || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Set canvas size based on floor plan dimensions
    const maxWidth = Math.max(
      ...floorPlanData.elements
        .filter((e) => e.type === "wall" || e.type === "room")
        .flatMap((e) => [e.start?.[0] || 0, e.end?.[0] || 0, (e.position?.[0] ?? 0) + (e.size?.[0] ?? 0)]),
    )

    const maxHeight = Math.max(
      ...floorPlanData.elements
        .filter((e) => e.type === "wall" || e.type === "room")
        .flatMap((e) => [e.start?.[1] || 0, e.end?.[1] || 0, (e.position?.[1] ?? 0) + (e.size?.[1] ?? 0)]),
    )

    canvas.width = maxWidth * scale + 100
    canvas.height = maxHeight * scale + 100

    // Set origin to bottom-left with padding
    ctx.translate(50, canvas.height - 50)
    ctx.scale(1, -1) // Flip y-axis to make origin at bottom-left

    // Draw grid
    drawGrid(ctx, maxWidth, maxHeight, scale)

    // Draw elements
    floorPlanData.elements.forEach((element) => {
      drawElement(ctx, element, scale)
    })
  }, [floorPlanData, scale])

  const drawGrid = (ctx: CanvasRenderingContext2D, width: number, height: number, scale: number) => {
    ctx.strokeStyle = "#e5e5e5"
    ctx.lineWidth = 0.5

    // Draw horizontal grid lines
    for (let y = 0; y <= height; y++) {
      ctx.beginPath()
      ctx.moveTo(0, y * scale)
      ctx.lineTo(width * scale, y * scale)
      ctx.stroke()
    }

    // Draw vertical grid lines
    for (let x = 0; x <= width; x++) {
      ctx.beginPath()
      ctx.moveTo(x * scale, 0)
      ctx.lineTo(x * scale, height * scale)
      ctx.stroke()
    }
  }

  const drawElement = (ctx: CanvasRenderingContext2D, element: FloorPlanElement, scale: number) => {
    switch (element.type) {
      case "room":
        drawRoom(ctx, element, scale)
        break
      case "wall":
        drawWall(ctx, element, scale)
        break
      case "door":
        drawDoor(ctx, element, scale)
        break
      case "window":
        drawWindow(ctx, element, scale)
        break
      default:
        console.warn(`Unknown element type: ${element.type}`)
    }
  }

  const drawRoom = (ctx: CanvasRenderingContext2D, room: FloorPlanElement, scale: number) => {
    if (!room.position || !room.size) return

    ctx.fillStyle = "rgba(200, 230, 255, 0.3)"
    ctx.strokeStyle = "#aaa"
    ctx.lineWidth = 1

    const [x, y] = room.position
    const [width, height] = room.size

    ctx.fillRect(x * scale, y * scale, width * scale, height * scale)
    ctx.strokeRect(x * scale, y * scale, width * scale, height * scale)

    // Draw room label
    ctx.save()
    ctx.scale(1, -1) // Flip back for text
    ctx.fillStyle = "#666"
    ctx.font = "14px Inter, system-ui, sans-serif"
    ctx.fillText(room.id || "Room", (x + width / 2) * scale - 20, -(y + height / 2) * scale + 5)
    ctx.restore()
  }

  const drawWall = (ctx: CanvasRenderingContext2D, wall: FloorPlanElement, scale: number) => {
    if (!wall.start || !wall.end) return

    ctx.strokeStyle = "#333"
    ctx.lineWidth = 8

    const [x1, y1] = wall.start
    const [x2, y2] = wall.end

    ctx.beginPath()
    ctx.moveTo(x1 * scale, y1 * scale)
    ctx.lineTo(x2 * scale, y2 * scale)
    ctx.stroke()
  }

  const drawDoor = (ctx: CanvasRenderingContext2D, door: FloorPlanElement, scale: number) => {
    if (!door.position || !door.width) return

    ctx.strokeStyle = "#8B4513"
    ctx.fillStyle = "#D2B48C"
    ctx.lineWidth = 2

    const [x, y] = door.position
    const width = door.width

    // Simplified door representation
    ctx.fillRect(x * scale - (width * scale) / 2, y * scale - 5, width * scale, 10)
    ctx.strokeRect(x * scale - (width * scale) / 2, y * scale - 5, width * scale, 10)
  }

  const drawWindow = (ctx: CanvasRenderingContext2D, window: FloorPlanElement, scale: number) => {
    if (!window.position || !window.width) return

    ctx.strokeStyle = "#87CEEB"
    ctx.fillStyle = "rgba(135, 206, 235, 0.5)"
    ctx.lineWidth = 2

    const [x, y] = window.position
    const width = window.width

    // Simplified window representation
    ctx.fillRect(x * scale - (width * scale) / 2, y * scale - 3, width * scale, 6)
    ctx.strokeRect(x * scale - (width * scale) / 2, y * scale - 3, width * scale, 6)
  }

  const handleZoomIn = () => {
    setScale((prev) => prev * 1.2)
  }

  const handleZoomOut = () => {
    setScale((prev) => prev / 1.2)
  }

  const handleResetZoom = () => {
    setScale(40)
  }

  return (
    <div className="relative h-full" ref={containerRef}>
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
            <canvas ref={canvasRef} className="min-w-full min-h-full" />
          </div>
        </div>
      )}
    </div>
  )
}
