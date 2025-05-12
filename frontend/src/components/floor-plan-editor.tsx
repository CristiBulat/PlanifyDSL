"use client"

import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import type { FloorPlanData, FloorPlanElement } from "@/lib/types"
import { Trash2, MousePointer, Plus, ZoomIn, ZoomOut, Maximize, Save } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { parseFloorPlan } from "@/lib/api"

interface FloorPlanEditorProps {
  floorPlanData: FloorPlanData | null
  onUpdate: (data: FloorPlanData) => void
}

export default function FloorPlanEditor({ floorPlanData, onUpdate }: FloorPlanEditorProps) {
  const svgContainerRef = useRef<HTMLDivElement>(null)
  const [selectedElement, setSelectedElement] = useState<string | null>(null)
  const [editMode, setEditMode] = useState<"select" | "add">("select")
  const [addElementType, setAddElementType] = useState<string>("wall")
  const [scale, setScale] = useState<number>(1) // Scale factor for SVG
  const [timestamp, setTimestamp] = useState<number>(Date.now()) // For cache busting
  const [dragging, setDragging] = useState<boolean>(false)
  const [dragStart, setDragStart] = useState<{x: number, y: number} | null>(null)

  // Local copy of floor plan data for editing
  const [localFloorPlanData, setLocalFloorPlanData] = useState<FloorPlanData | null>(floorPlanData)

  useEffect(() => {
    setLocalFloorPlanData(floorPlanData)
    if (floorPlanData) {
      setTimestamp(Date.now())
    }
  }, [floorPlanData])

  // Function to get cursor position in SVG coordinates
  const getSvgCoordinates = (event: React.MouseEvent): {x: number, y: number} | null => {
    if (!svgContainerRef.current) return null

    const svgElement = svgContainerRef.current.querySelector('svg')
    if (!svgElement) return null

    const svgPoint = svgElement.createSVGPoint()
    svgPoint.x = event.clientX
    svgPoint.y = event.clientY

    // Get the transformation matrix from screen to SVG coordinates
    const ctm = svgElement.getScreenCTM()
    if (!ctm) return null

    const transformedPoint = svgPoint.matrixTransform(ctm.inverse())
    return {
      x: transformedPoint.x / 10, // Convert from pixels to meters (assuming scale factor of 10)
      y: transformedPoint.y / 10
    }
  }

  const handleSvgClick = (e: React.MouseEvent) => {
    if (!localFloorPlanData) return

    const coords = getSvgCoordinates(e)
    if (!coords) return

    if (editMode === "select") {
      // Find clicked element by checking the target and its parent elements
      let target = e.target as Element
      let elementId = null

      // Check if the target or any of its parents has a data-id attribute
      while (target && !elementId) {
        if (target.getAttribute('data-id')) {
          elementId = target.getAttribute('data-id')
          break
        }
        target = target.parentElement as Element
      }

      setSelectedElement(elementId)
    } else if (editMode === "add") {
      // Add new element at the clicked coordinates
      addNewElement(coords.x, coords.y)
    }
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!selectedElement || editMode !== "select") return

    const coords = getSvgCoordinates(e)
    if (!coords) return

    setDragging(true)
    setDragStart(coords)
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!dragging || !dragStart || !selectedElement || !localFloorPlanData) return

    const coords = getSvgCoordinates(e)
    if (!coords) return

    // Calculate the distance moved
    const deltaX = coords.x - dragStart.x
    const deltaY = coords.y - dragStart.y

    // Update the element position
    const updatedElements = localFloorPlanData.elements.map(element => {
      if (element.id === selectedElement) {
        if (element.position) {
          return {
            ...element,
            position: [element.position[0] + deltaX, element.position[1] + deltaY]
          }
        } else if (element.start && element.end) {
          return {
            ...element,
            start: [element.start[0] + deltaX, element.start[1] + deltaY],
            end: [element.end[0] + deltaX, element.end[1] + deltaY]
          }
        }
      }
      return element
    })

    setLocalFloorPlanData({
      ...localFloorPlanData,
      elements: updatedElements
    })

    // Reset drag start position
    setDragStart(coords)
  }

  const handleMouseUp = () => {
    setDragging(false)
    setDragStart(null)
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
        newElement.height = 0.5 // Default height
        newElement.direction = "right" // Default direction
        break
      case "window":
        newElement.position = [x, y]
        newElement.width = 1.5 // Default width
        newElement.height = 0.3 // Default height
        break
      case "bed":
        newElement.position = [x, y]
        newElement.width = 3 // Default width
        newElement.height = 5 // Default height
        break
      case "table":
        newElement.position = [x, y]
        newElement.width = 2 // Default width
        newElement.height = 2 // Default height
        break
      case "chair":
        newElement.position = [x, y]
        newElement.width = 1 // Default width
        newElement.height = 1 // Default height
        break
      case "stairs":
        newElement.position = [x, y]
        newElement.width = 2 // Default width
        newElement.height = 4 // Default height
        break
      case "elevator":
        newElement.position = [x, y]
        newElement.width = 2 // Default width
        newElement.height = 2 // Default height
        break
    }

    const updatedData = {
      ...localFloorPlanData,
      elements: [...localFloorPlanData.elements, newElement],
    }

    setLocalFloorPlanData(updatedData)
    setSelectedElement(newElement.id)
    setEditMode("select") // Switch back to select mode after adding
    setTimestamp(Date.now()) // Force SVG refresh
  }

  const handleDeleteElement = () => {
    if (!localFloorPlanData || !selectedElement) return

    const updatedElements = localFloorPlanData.elements.filter((element) => element.id !== selectedElement)

    const updatedData = {
      ...localFloorPlanData,
      elements: updatedElements,
    }

    setLocalFloorPlanData(updatedData)
    setSelectedElement(null)
    setTimestamp(Date.now()) // Force SVG refresh
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
    setTimestamp(Date.now()) // Force SVG refresh
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
              <div className="space-y-1 col-span-2">
                <label className="text-xs font-medium text-gray-700">Label</label>
                <Input
                  value={element.label || ""}
                  onChange={(e) => handleElementPropertyChange("label", e.target.value)}
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

          {["door", "window", "bed", "table", "chair", "stairs", "elevator"].includes(element.type) && element.position && (
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
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Height</label>
                <Input
                  type="number"
                  value={element.height || 1}
                  onChange={(e) => handleElementPropertyChange("height", e.target.value)}
                  className="h-8"
                />
              </div>

              {element.type === "door" && (
                <div className="space-y-1 col-span-2">
                  <label className="text-xs font-medium text-gray-700">Direction</label>
                  <Select
                    value={element.direction || "right"}
                    onValueChange={(value) => handleElementPropertyChange("direction", value)}
                  >
                    <SelectTrigger className="h-8">
                      <SelectValue placeholder="Direction" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="left">Left</SelectItem>
                      <SelectItem value="right">Right</SelectItem>
                      <SelectItem value="up">Up</SelectItem>
                      <SelectItem value="down">Down</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
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
    setScale(1)
  }

  const handleSaveChanges = async () => {
    if (!localFloorPlanData) return

    // Generate DSL code from the current floor plan data
    const dslCode = generateDslCode(localFloorPlanData)

    try {
      // Parse the DSL code to get updated SVG and normalized data
      const updatedData = await parseFloorPlan(dslCode)

      // Update the parent component with the new data
      onUpdate(updatedData)

      // Update local state
      setLocalFloorPlanData(updatedData)
      setTimestamp(Date.now())
    } catch (error) {
      console.error("Error saving changes:", error)
      alert("Error saving changes. Please check the console for details.")
    }
  }

  // Function to generate DSL code from FloorPlanData
  const generateDslCode = (data: FloorPlanData): string => {
    if (!data || !data.elements || data.elements.length === 0) return "";

    let code = "# size: 1000 x 1000\n\n";

    data.elements.forEach(element => {
      switch (element.type) {
        case "room":
          code += `Room {\n`;
          code += `    id: "${element.id}";\n`;
          if (element.label) code += `    label: "${element.label}";\n`;
          if (element.position && element.size) {
            code += `    size: [${element.size[0]}, ${element.size[1]}];\n`;
            code += `    position: [${element.position[0]}, ${element.position[1]}];\n`;
          }
          code += `}\n\n`;
          break;
        case "wall":
          code += `Wall {\n`;
          code += `    id: "${element.id}";\n`;
          if (element.start && element.end) {
            code += `    start: [${element.start[0]}, ${element.start[1]}];\n`;
            code += `    end: [${element.end[0]}, ${element.end[1]}];\n`;
          }
          code += `}\n\n`;
          break;
        case "door":
          code += `Door {\n`;
          code += `    id: "${element.id}";\n`;
          if (element.position) {
            code += `    position: [${element.position[0]}, ${element.position[1]}];\n`;
          }
          if (element.width) code += `    width: ${element.width};\n`;
          if (element.height) code += `    height: ${element.height};\n`;
          if (element.direction) code += `    direction: "${element.direction}";\n`;
          code += `}\n\n`;
          break;
        case "window":
          code += `Window {\n`;
          code += `    id: "${element.id}";\n`;
          if (element.position) {
            code += `    position: [${element.position[0]}, ${element.position[1]}];\n`;
          }
          if (element.width) code += `    width: ${element.width};\n`;
          if (element.height) code += `    height: ${element.height};\n`;
          code += `}\n\n`;
          break;
        case "bed":
        case "table":
        case "chair":
        case "stairs":
        case "elevator":
          const typeName = element.type.charAt(0).toUpperCase() + element.type.slice(1);
          code += `${typeName} {\n`;
          code += `    id: "${element.id}";\n`;
          if (element.position) {
            code += `    position: [${element.position[0]}, ${element.position[1]}];\n`;
          }
          if (element.width) code += `    width: ${element.width};\n`;
          if (element.height) code += `    height: ${element.height};\n`;
          code += `}\n\n`;
          break;
      }
    });

    return code;
  };

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
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleSaveChanges}
                  className="h-8 bg-green-600 hover:bg-green-700"
                >
                  <Save className="h-4 w-4 mr-1" />
                  Save Changes
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
                    <SelectItem value="bed">Bed</SelectItem>
                    <SelectItem value="table">Table</SelectItem>
                    <SelectItem value="chair">Chair</SelectItem>
                    <SelectItem value="stairs">Stairs</SelectItem>
                    <SelectItem value="elevator">Elevator</SelectItem>
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

            <div
              className="min-h-[400px] overflow-auto"
              ref={svgContainerRef}
              onClick={handleSvgClick}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
            >
              {localFloorPlanData.svg_url && (
                <div
                  style={{
                    transform: `scale(${scale})`,
                    transformOrigin: "top left",
                    transition: "transform 0.2s",
                    cursor: editMode === "add" ? "crosshair" : (dragging ? "grabbing" : "default")
                  }}
                >
                  <img
                    src={`http://localhost:5001${localFloorPlanData.svg_url}?t=${timestamp}`}
                    alt="Floor Plan"
                    className="min-w-full min-h-full"
                    draggable="false"
                  />
                </div>
              )}
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