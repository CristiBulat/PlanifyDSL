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
import { Loader2, Code2, Grid2X2, Wand2 } from "lucide-react"
import { useDslState } from "@/lib/dsl-state"

export default function Home() {
  const { dslCode, setDslCode, generateRandomDslCode } = useDslState()
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

  const handleEditorUpdate = (data: FloorPlanData) => {
    setFloorPlanData(data)

    const generatedDSL = generateDslCode(data)
    setDslCode(generatedDSL)
  }

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
    <div className="flex flex-col min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container py-4 mx-auto">
          <h1 className="text-2xl font-bold">2D Floor Planning Application</h1>
          <p className="text-gray-500">Design floor plans using a domain-specific language</p>
        </div>
      </header>

      <main className="container flex flex-row flex-1 gap-6 px-4 py-6 mx-auto">
        {/* Left Column: DSL Code Editor */}
        <div className="flex flex-col w-full max-w-md">
          <Card className="flex flex-col flex-1">
            <CardHeader className="pb-3">
              <div className="flex items-center">
                <Code2 className="w-5 h-5 mr-2 text-gray-500" />
                <CardTitle>DSL Code</CardTitle>
              </div>
              <CardDescription>Write your floor plan code using the DSL</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col flex-1 space-y-4">
              <div className="border rounded-md bg-gray-50 max-h-[65vh] overflow-y-auto">
                <CodeEditor value={dslCode} onChange={handleCodeChange} />
              </div>
              <div className="flex items-center justify-between gap-2 mt-2">
                <Button 
                  onClick={generateRandomDslCode} 
                  className="text-white bg-purple-600 hover:bg-purple-700"
                >
                  <Wand2 className="w-4 h-4 mr-2" />
                  Generate DSL
                </Button>
                <Button onClick={handleParse} disabled={isLoading} className="text-white bg-blue-600 hover:bg-blue-700">
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    "Parse & Render"
                  )}
                </Button>
                {error && <div className="ml-2 overflow-hidden text-sm text-red-500 text-ellipsis">{error}</div>}
              </div>
            </CardContent>
          </Card>
        </div>
        {/* Right Column: Tabs for Floor Plan Viewer and Editor */}
        <div className="flex flex-col flex-1">
          <Card className="flex flex-col flex-1">
            <CardHeader className="pb-3">
              <div className="flex items-center">
                <Grid2X2 className="w-5 h-5 mr-2 text-gray-500" />
                <CardTitle>Floor Plan</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="flex flex-col flex-1">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col flex-1 w-full">
                <TabsList className="grid w-full grid-cols-2 mb-4">
                  <TabsTrigger value="view">Viewer</TabsTrigger>
                  <TabsTrigger value="edit">Editor</TabsTrigger>
                </TabsList>
                <div className="flex items-center justify-center flex-1 min-h-0 p-4 rounded-lg bg-gray-50">
                  <TabsContent value="view" className="w-full h-full">
                    <FloorPlanViewer floorPlanData={floorPlanData} />
                  </TabsContent>
                  <TabsContent value="edit" className="w-full h-full">
                    <FloorPlanEditor floorPlanData={floorPlanData} onUpdate={handleEditorUpdate} />
                  </TabsContent>
                </div>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}