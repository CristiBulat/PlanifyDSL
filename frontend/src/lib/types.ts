export interface FloorPlanElement {
  id: string;
  type: string;
  position?: [number, number];
  size?: [number, number];
  start?: [number, number];
  end?: [number, number];
  width?: number;
  height?: number;
  wall?: string;
  direction?: string;
  [key: string]: any;
}

export interface FloorPlanData {
  elements: FloorPlanElement[];
  svg_url?: string; // Make sure this is defined
}