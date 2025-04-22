"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import FloorPlanEditor from "@/components/floor-plan-editor"
import FloorPlanViewer from "@/components/floor-plan-viewer"
import CodeEditor from "@/components/code-editor"
import { parseFloorPlan } from "@/lib/api"
import type { FloorPlanData } from "@/lib/types"
import { Loader2, Code2, Grid2X2 } from "lucide-react"

export default function Home() {
  const [dslCode, setDslCode] = useState<string>(`// Example DSL code
Room {
  id: "living_room";
  size: {10m, 8m};
  position: {0m, 0m};
}

Wall {
  id: "north_wall";
  start: {0m, 0m};
  end: {10m, 0m};
}

Wall {
  id: "east_wall";
  start: {10m, 0m};
  end: {10m, 8m};
}

Wall {
  id: "south_wall";
  start: {0m, 8m};
  end: {10m, 8m};
}

Wall {
  id: "west_wall";
  start: {0m, 0m};
  end: {0m, 8m};
}

Door {
  id: "main_door";
  wall: "south_wall";
  position: {5m, 8m};
  width: 1m;
}

Window {
  id: "living_window";
  wall: "east_wall";
  position: {10m, 4m};
  width: 2m;
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
                      <FloorPlanEditor floorPlanData={floorPlanData} onUpdate={(data) => setFloorPlanData(data)} />
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
