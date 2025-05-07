export interface FloorPlanElement {
  id: string
  type: "room" | "wall" | "door" | "window"
  position?: [number, number]
  size?: [number, number]
  start?: [number, number]
  end?: [number, number]
  width?: number
  height?: number
  wall?: string
  [key: string]: any
}

export interface FloorPlanData {
  elements: FloorPlanElement[]
}
