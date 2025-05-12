"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import FloorPlanEditor from "@/components/floor-plan-editor"
import FloorPlanViewer from "@/components/floor-plan-viewer"
import CodeEditor from "@/components/code-editor"
import { parseFloorPlan } from "@/lib/api"
import type { FloorPlanData, FloorPlanElement } from "@/lib/types"
import { Loader2, Code2, Grid2X2 } from "lucide-react"

export default function Home() {
  const [dslCode, setDslCode] = useState<string>(`# size: 1000 x 1000

// Bedroom
Room {
    id: "bedroom";
    label: "Bedroom";
    size: [300, 250];
    position: [0, 0];
}

Room {
    id: "living";
    label: "Living-Room";
    size: [400, 300];
    position: [0, 250];
}

Room {
    id: "bathroom";
    label: "Bathroom";
    size: [200, 150];
    position: [300, 0];
}

Room {
    id: "kitchen";
    label: "kitchen";
    size: [300, 100];
    position: [300, 150];
}

Window {
    id: "window_east";
    position: [0, 100];
    width: 10;
    height: 40;
}

// Bed
Bed {
    id: "bed";
    position: [100, 10];
    width: 100;
    height: 150;
}

// Door
Door {
    id: "bedroom_door";
    position: [70, 250];
    width: 40;
    height: 15;
    direction: "up";
}

// Bedside Table
Table {
    id: "bedside_table";
    position: [25, 10];
    width: 50;
    height: 50;
}

Chair {
    id: "sofa";
    position: [35, 70];
    width: 30;
    height: 15;
}

Stairs {
    id: "stairs";
    position: [400, 400];
    width: 30;
    height: 15;
}

Elevator {
    id: "elevator";
    position: [500, 500];
    width: 30;
    height: 15;
}`)
  const [floorPlanData, setFloorPlanData] = useState<FloorPlanData | null>(null)
  const [activeTab, setActiveTab] = useState<string>("view")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const handleCodeChange = (value: string) => {
    setDslCode(value)
  }

  const handleParse = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await parseFloorPlan(dslCode)
      setFloorPlanData(data)
      setActiveTab("view")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to parse floor plan")
    } finally {
      setIsLoading(false)
    }
  }

  // Handle updates from the editor
  const handleEditorUpdate = (data: FloorPlanData) => {
    setFloorPlanData(data)

    // Generate DSL code from the floor plan data
    const generatedDSL = generateDslCode(data)
    setDslCode(generatedDSL)
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
          // Capitalize first letter for type name
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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto py-4">
          <h1 className="text-2xl font-bold">2D Floor Planning Application</h1>
          <p className="text-gray-500">Design floor plans using a domain-specific language</p>
        </div>
      </header>

      <main className="container mx-auto py-6 px-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: DSL Code Editor */}
          <div className="lg:col-span-1">
            <Card className="h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center">
                  <Code2 className="h-5 w-5 mr-2 text-gray-500" />
                  <CardTitle>DSL Code</CardTitle>
                </div>
                <CardDescription>Write your floor plan code using the DSL</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border rounded-md bg-gray-50">
                  <CodeEditor value={dslCode} onChange={handleCodeChange} />
                </div>

                <div className="flex justify-between items-center">
                  <Button onClick={handleParse} disabled={isLoading} className="bg-blue-600 hover:bg-blue-700">
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      "Parse & Render"
                    )}
                  </Button>

                  {error && <div className="text-red-500 text-sm ml-2 overflow-hidden text-ellipsis">{error}</div>}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Tabs for Floor Plan Viewer and Editor */}
          <div className="lg:col-span-2">
            <Card className="h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center">
                  <Grid2X2 className="h-5 w-5 mr-2 text-gray-500" />
                  <CardTitle>Floor Plan</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                  <TabsList className="grid w-full grid-cols-2 mb-4">
                    <TabsTrigger value="view">Viewer</TabsTrigger>
                    <TabsTrigger value="edit">Editor</TabsTrigger>
                  </TabsList>
                  <div className="bg-gray-50 rounded-lg min-h-[600px] p-4">
                    <TabsContent value="view" className="mt-0 h-full">
                      <FloorPlanViewer floorPlanData={floorPlanData} />
                    </TabsContent>
                    <TabsContent value="edit" className="mt-0 h-full">
                      <FloorPlanEditor floorPlanData={floorPlanData} onUpdate={handleEditorUpdate} />
                    </TabsContent>
                  </div>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}