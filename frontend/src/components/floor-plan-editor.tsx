"use client"

import type React from "react"

import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import type { FloorPlanData, FloorPlanElement } from "@/lib/types"
import { Trash2, MousePointer, Plus, ZoomIn, ZoomOut, Maximize } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface FloorPlanEditorProps {
  floorPlanData: FloorPlanData | null
  onUpdate: (data: FloorPlanData) => void
}

export default function FloorPlanEditor({ floorPlanData, onUpdate }: FloorPlanEditorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [selectedElement, setSelectedElement] = useState<string | null>(null)
  const [editMode, setEditMode] = useState<"select" | "add">("select")
  const [addElementType, setAddElementType] = useState<string>("wall")
  const [scale, setScale] = useState<number>(40) // pixels per meter

  // Local copy of floor plan data for editing
  const [localFloorPlanData, setLocalFloorPlanData] = useState<FloorPlanData | null>(floorPlanData)

  useEffect(() => {
    setLocalFloorPlanData(floorPlanData)
  }, [floorPlanData])

  useEffect(() => {
    if (!localFloorPlanData || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Set canvas size based on floor plan dimensions
    const maxWidth = Math.max(
      ...localFloorPlanData.elements
        .filter((e) => e.type === "wall" || e.type === "room")
        .flatMap((e) => [e.start?.[0] || 0, e.end?.[0] || 0, (e.position?.[0] ?? 0) + (e.size?.[0] ?? 0)]),
    )

    const maxHeight = Math.max(
      ...localFloorPlanData.elements
        .filter((e) => e.type === "wall" || e.type === "room")
        .flatMap((e) => [
          e.start?.[1] || 0,
          e.end?.[1] || 0,
          e.position && e.size ? e.position[1] + (e.size[1] || 0) : 0,
        ]),
    )

    canvas.width = maxWidth * scale + 100
    canvas.height = maxHeight * scale + 100

    // Set origin to bottom-left with padding
    ctx.translate(50, canvas.height - 50)
    ctx.scale(1, -1) // Flip y-axis to make origin at bottom-left

    // Draw grid
    drawGrid(ctx, maxWidth, maxHeight, scale)

    // Draw elements
    localFloorPlanData.elements.forEach((element) => {
      const isSelected = element.id === selectedElement
      drawElement(ctx, element, scale, isSelected)
    })
  }, [localFloorPlanData, selectedElement, scale])

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

  const drawElement = (ctx: CanvasRenderingContext2D, element: FloorPlanElement, scale: number, isSelected = false) => {
    // Set highlight for selected element
    if (isSelected) {
      ctx.shadowColor = "rgba(59, 130, 246, 0.5)"
      ctx.shadowBlur = 10
    }

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

    // Reset shadow
    ctx.shadowColor = "transparent"
    ctx.shadowBlur = 0
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

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!localFloorPlanData || !canvasRef.current) return

    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()

    // Calculate click position in canvas coordinates
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    // Convert to floor plan coordinates (accounting for the translation and scale)
    const floorPlanX = (x - 50) / scale
    const floorPlanY = (canvas.height - y - 50) / scale

    if (editMode === "select") {
      // Find clicked element
      const clickedElement = findElementAtPosition(floorPlanX, floorPlanY)
      setSelectedElement(clickedElement?.id || null)
    } else if (editMode === "add") {
      // Add new element
      addNewElement(floorPlanX, floorPlanY)
    }
  }

  const findElementAtPosition = (x: number, y: number): FloorPlanElement | undefined => {
    if (!localFloorPlanData) return undefined

    // Check rooms first (they're larger and easier to click)
    for (const element of localFloorPlanData.elements) {
      if (element.type === "room" && element.position && element.size) {
        const [roomX, roomY] = element.position
        const [width, height] = element.size

        if (x >= roomX && x <= roomX + width && y >= roomY && y <= roomY + height) {
          return element
        }
      }
    }

    // Then check other elements
    for (const element of localFloorPlanData.elements) {
      if (element.type === "wall" && element.start && element.end) {
        // Check if click is near the wall line
        const [x1, y1] = element.start
        const [x2, y2] = element.end

        // Calculate distance from point to line
        const distance = distanceToLine(x, y, x1, y1, x2, y2)
        if (distance < 0.5) {
          // Within 0.5 meters
          return element
        }
      } else if ((element.type === "door" || element.type === "window") && element.position && element.width) {
        const [elemX, elemY] = element.position
        const width = element.width

        if (Math.abs(x - elemX) <= width / 2 && Math.abs(y - elemY) <= 0.3) {
          return element
        }
      }
    }

    return undefined
  }

  const distanceToLine = (x: number, y: number, x1: number, y1: number, x2: number, y2: number): number => {
    const A = x - x1
    const B = y - y1
    const C = x2 - x1
    const D = y2 - y1

    const dot = A * C + B * D
    const lenSq = C * C + D * D
    let param = -1

    if (lenSq !== 0) {
      param = dot / lenSq
    }

    let xx, yy

    if (param < 0) {
      xx = x1
      yy = y1
    } else if (param > 1) {
      xx = x2
      yy = y2
    } else {
      xx = x1 + param * C
      yy = y1 + param * D
    }

    const dx = x - xx
    const dy = y - yy

    return Math.sqrt(dx * dx + dy * dy)
  }

  const addNewElement = (x: number, y: number) => {
    if (!localFloorPlanData) return

    const newElement: FloorPlanElement = {
      id: `${addElementType}_${Date.now()}`,
      type: addElementType as any,
    }

    switch (addElementType) {
      case "room":
        newElement.position = [x, y]
        newElement.size = [5, 4] // Default size
        break
      case "wall":
        newElement.start = [x, y]
        newElement.end = [x + 5, y] // Default length
        break
      case "door":
        newElement.position = [x, y]
        newElement.width = 1 // Default width
        break
      case "window":
        newElement.position = [x, y]
        newElement.width = 1.5 // Default width
        break
    }

    const updatedData = {
      ...localFloorPlanData,
      elements: [...localFloorPlanData.elements, newElement],
    }

    setLocalFloorPlanData(updatedData)
    onUpdate(updatedData)
    setSelectedElement(newElement.id)
    setEditMode("select") // Switch back to select mode after adding
  }

  const handleDeleteElement = () => {
    if (!localFloorPlanData || !selectedElement) return

    const updatedElements = localFloorPlanData.elements.filter((element) => element.id !== selectedElement)

    const updatedData = {
      ...localFloorPlanData,
      elements: updatedElements,
    }

    setLocalFloorPlanData(updatedData)
    onUpdate(updatedData)
    setSelectedElement(null)
  }

  const handleElementPropertyChange = (property: string, value: any) => {
    if (!localFloorPlanData || !selectedElement) return

    const updatedElements = localFloorPlanData.elements.map((element) => {
      if (element.id === selectedElement) {
        // Handle different property types
        if (property.includes(".")) {
          // Handle nested properties like 'position.0'
          const [mainProp, index] = property.split(".")

          if (!element[mainProp]) {
            element[mainProp] = []
          }

          element[mainProp][Number.parseInt(index)] = Number.parseFloat(value)
        } else if (property === "width" || property === "height") {
          // Handle numeric properties
          element[property] = Number.parseFloat(value)
        } else {
          // Handle other properties
          element[property] = value
        }
      }
      return element
    })

    const updatedData = {
      ...localFloorPlanData,
      elements: updatedElements,
    }

    setLocalFloorPlanData(updatedData)
    onUpdate(updatedData)
  }

  const getSelectedElementDetails = () => {
    if (!localFloorPlanData || !selectedElement) return null

    return localFloorPlanData.elements.find((element) => element.id === selectedElement)
  }

  const renderElementProperties = () => {
    const element = getSelectedElementDetails()
    if (!element) return null

    return (
      <div className="space-y-4 mt-4">
        <h3 className="font-medium text-sm text-gray-500 uppercase tracking-wider">Properties</h3>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <label className="text-xs font-medium text-gray-700">ID</label>
            <Input
              value={element.id || ""}
              onChange={(e) => handleElementPropertyChange("id", e.target.value)}
              className="h-8"
            />
          </div>

          {element.type === "room" && element.position && element.size && (
            <>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Position X</label>
                <Input
                  type="number"
                  value={element.position[0]}
                  onChange={(e) => handleElementPropertyChange("position.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Position Y</label>
                <Input
                  type="number"
                  value={element.position[1]}
                  onChange={(e) => handleElementPropertyChange("position.1", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Width</label>
                <Input
                  type="number"
                  value={element.size[0]}
                  onChange={(e) => handleElementPropertyChange("size.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Height</label>
                <Input
                  type="number"
                  value={element.size[1]}
                  onChange={(e) => handleElementPropertyChange("size.1", e.target.value)}
                  className="h-8"
                />
              </div>
            </>
          )}

          {element.type === "wall" && element.start && element.end && (
            <>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Start X</label>
                <Input
                  type="number"
                  value={element.start[0]}
                  onChange={(e) => handleElementPropertyChange("start.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Start Y</label>
                <Input
                  type="number"
                  value={element.start[1]}
                  onChange={(e) => handleElementPropertyChange("start.1", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">End X</label>
                <Input
                  type="number"
                  value={element.end[0]}
                  onChange={(e) => handleElementPropertyChange("end.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">End Y</label>
                <Input
                  type="number"
                  value={element.end[1]}
                  onChange={(e) => handleElementPropertyChange("end.1", e.target.value)}
                  className="h-8"
                />
              </div>
            </>
          )}

          {(element.type === "door" || element.type === "window") && element.position && (
            <>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Position X</label>
                <Input
                  type="number"
                  value={element.position[0]}
                  onChange={(e) => handleElementPropertyChange("position.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Position Y</label>
                <Input
                  type="number"
                  value={element.position[1]}
                  onChange={(e) => handleElementPropertyChange("position.1", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Width</label>
                <Input
                  type="number"
                  value={element.width || 1}
                  onChange={(e) => handleElementPropertyChange("width", e.target.value)}
                  className="h-8"
                />
              </div>
            </>
          )}
        </div>

        <Button variant="destructive" size="sm" onClick={handleDeleteElement} className="mt-2 w-full">
          <Trash2 className="h-4 w-4 mr-2" />
          Delete Element
        </Button>
      </div>
    )
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
    <div className="relative">
      {!localFloorPlanData ? (
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
          <p className="text-gray-500 text-center">Parse your DSL code to use the editor</p>
          <p className="text-gray-400 text-sm text-center mt-1">Click the "Parse & Render" button to start editing</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-3 border rounded-md bg-white">
            <div className="p-2 border-b flex justify-between items-center">
              <div className="flex gap-2">
                <Button
                  variant={editMode === "select" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setEditMode("select")}
                  className="h-8"
                >
                  <MousePointer className="h-4 w-4 mr-1" />
                  Select
                </Button>
                <Button
                  variant={editMode === "add" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setEditMode("add")}
                  className="h-8"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Add
                </Button>
              </div>

              {editMode === "add" && (
                <Select value={addElementType} onValueChange={setAddElementType}>
                  <SelectTrigger className="w-[180px] h-8">
                    <SelectValue placeholder="Element Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="room">Room</SelectItem>
                    <SelectItem value="wall">Wall</SelectItem>
                    <SelectItem value="door">Door</SelectItem>
                    <SelectItem value="window">Window</SelectItem>
                  </SelectContent>
                </Select>
              )}

              <div className="flex gap-1">
                <Button variant="outline" size="icon" onClick={handleZoomIn} className="h-8 w-8">
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon" onClick={handleZoomOut} className="h-8 w-8">
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon" onClick={handleResetZoom} className="h-8 w-8">
                  <Maximize className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="min-h-[400px] overflow-auto">
              <canvas ref={canvasRef} className="min-w-full min-h-full" onClick={handleCanvasClick} />
            </div>
          </div>

          <div>
            <Card>
              <CardContent className="p-4">
                <h3 className="font-medium mb-4">Element Inspector</h3>

                {selectedElement ? (
                  renderElementProperties()
                ) : (
                  <p className="text-gray-500 text-sm">
                    {editMode === "select"
                      ? "Select an element to edit its properties"
                      : "Click on the canvas to add a new element"}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}
