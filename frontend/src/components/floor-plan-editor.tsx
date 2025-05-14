"use client"

import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import type { FloorPlanData, FloorPlanElement } from "@/lib/types"
import { Trash2, MousePointer, Plus, ZoomIn, ZoomOut, Maximize, Save, X, Download } from "lucide-react"
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
  const [addElementType, setAddElementType] = useState<string>("room")
  const [scale, setScale] = useState<number>(0.694444)
  const [timestamp, setTimestamp] = useState<number>(Date.now())
  const [dragging, setDragging] = useState<boolean>(false)
  const [dragStart, setDragStart] = useState<{x: number, y: number} | null>(null)
  const [svgContent, setSvgContent] = useState<string>("")

  const [localFloorPlanData, setLocalFloorPlanData] = useState<FloorPlanData | null>(floorPlanData)
  
  // Form state for editing properties (separate from actual data)
  const [formValues, setFormValues] = useState<any>(null)
  
  const [showInspector, setShowInspector] = useState<boolean>(false);

  useEffect(() => {
    setLocalFloorPlanData(floorPlanData)
    if (floorPlanData) {
      setTimestamp(Date.now())
    }
  }, [floorPlanData])

  useEffect(() => {
    if (localFloorPlanData?.svg_url) {
      fetch(`http://localhost:5001${localFloorPlanData.svg_url}?t=${timestamp}`)
        .then(response => response.text())
        .then(text => {
          // Add data-id attributes to SVG elements if they don't have them
          const enhancedSvg = enhanceSvgWithDataIds(text, localFloorPlanData.elements);
          setSvgContent(enhancedSvg);
        })
        .catch(error => console.error("Error fetching SVG:", error))
    }
  }, [localFloorPlanData?.svg_url, timestamp])

  // Function to add data-id attributes to SVG elements
  const enhanceSvgWithDataIds = (svgContent: string, elements: FloorPlanElement[]): string => {
    // Simple enhancement for debugging - this adds console log statements in the SVG
    // to help track element clicks
    let enhancedSvg = svgContent;
    
    // Return the original SVG if data-id attributes are already present
    if (svgContent.includes('data-id=')) {
      return svgContent;
    }
    
    // Map of element types to their likely SVG tag patterns
    const typeToTagMap: Record<string, string[]> = {
      room: ['rect', 'path'],
      wall: ['line'],
      door: ['path', 'line'],
      window: ['rect', 'line'],
      bed: ['rect', 'g'],
      table: ['rect', 'g'],
      chair: ['rect', 'g'],
      stairs: ['rect', 'g'],
      elevator: ['rect', 'g']
    };
    
    // For each element, try to find a matching SVG tag
    elements.forEach((element, index) => {
      if (!element.id || !element.type) return;
      
      // Get the possible tags for this element type
      const possibleTags = typeToTagMap[element.type] || ['rect', 'path', 'line', 'g'];
      
      // For each possible tag, add a data-id attribute to all matching elements
      possibleTags.forEach(tag => {
        // Create a unique identifier for the element in the SVG
        const tagRegex = new RegExp(`<${tag}\\s`, 'g');
        let matchCount = 0;
        
        // Replace each occurrence of the tag with the same tag plus a data-id attribute
        enhancedSvg = enhancedSvg.replace(tagRegex, (match) => {
          matchCount++;
          // Only add data-id to the nth occurrence matching this element's index
          if (matchCount === index + 1) {
            return `${match}data-id="${element.id}" data-type="${element.type}" `;
          }
          return match;
        });
      });
    });
    
    return enhancedSvg;
  };

  // When an element is selected, initialize the form values
  useEffect(() => {
    if (!selectedElement || !localFloorPlanData) {
      setFormValues(null);
      return;
    }
    
    const element = localFloorPlanData.elements.find(el => el.id === selectedElement);
    if (element) {
      // Clone the element to use as form values
      setFormValues(JSON.parse(JSON.stringify(element)));
    }
  }, [selectedElement, localFloorPlanData]);

  // Highlight selected element in the SVG
  useEffect(() => {
    if (!svgContent || !svgContainerRef.current) return;
    
    const updateSelectedElement = () => {
      const svgContainer = svgContainerRef.current;
      if (!svgContainer) return;

      // Remove selected class from all elements
      const elements = svgContainer.querySelectorAll('[data-id]');
      elements.forEach(el => {
        el.classList.remove('selected-element');
      });

      // Add selected class to selected element
      if (selectedElement) {
        const selectedEl = svgContainer.querySelector(`[data-id="${selectedElement}"]`);
        if (selectedEl) {
          selectedEl.classList.add('selected-element');
        }
      }
    };

    // Update immediately and after a short delay to ensure SVG is rendered
    updateSelectedElement();
    const timer = setTimeout(updateSelectedElement, 100);
    
    return () => clearTimeout(timer);
  }, [svgContent, selectedElement]);

  useEffect(() => {
    setShowInspector(editMode === "select" && !!selectedElement);
  }, [editMode, selectedElement]);

  // Improve SVG coordinate calculation
  const getSvgCoordinates = (event: React.MouseEvent): {x: number, y: number} | null => {
    if (!svgContainerRef.current) return null;

    // Find and get dimensions of the SVG element
    const svgElement = svgContainerRef.current.querySelector('svg');
    if (!svgElement) return null;

    const rect = svgElement.getBoundingClientRect();
    
    // Get click position relative to SVG element
    const clientX = event.clientX - rect.left;
    const clientY = event.clientY - rect.top;
    
    // Get viewBox to calculate proper scaling
    const viewBox = svgElement.getAttribute('viewBox');
    if (!viewBox) {
      // Fallback to simple scaling if no viewBox
      return {
        x: (clientX / scale) / 10,
        y: (clientY / scale) / 10
      };
    }
    
    // Parse viewBox values
    const [minX, minY, width, height] = viewBox.split(' ').map(Number);
    
    // Calculate the real coordinates based on viewBox
    return {
      x: minX + (clientX / rect.width) * width,
      y: minY + (clientY / rect.height) * height
    };
  }

  // Improved click handling with debugging
  const handleSvgClick = (e: React.MouseEvent) => {
    if (!localFloorPlanData) return;

    // Add debug output to see what element was clicked
    console.log("Clicked element:", e.target);
    
    if (editMode === "select") {
      // Find what element was clicked
      let clickedElement = null;
      let target = e.target as Element;
      
      // Check if the target itself has data-id
      if (target.hasAttribute('data-id')) {
        clickedElement = target.getAttribute('data-id');
      } else {
        // Walk up the DOM to find parent with data-id
        while (target && !clickedElement && target !== svgContainerRef.current) {
          if (target.hasAttribute('data-id')) {
            clickedElement = target.getAttribute('data-id');
            break;
          }
          target = target.parentElement!;
        }
      }
      
      // If we found an element, select it
      if (clickedElement) {
        console.log("Selected element:", clickedElement);
        setSelectedElement(clickedElement);
        setShowInspector(true);
      } else {
        // Debug: show where the click happened
        const coords = getSvgCoordinates(e);
        console.log("Click coordinates:", coords);
        
        // Try a different approach - check if we're near any element
        if (svgContainerRef.current && coords) {
          console.log("Trying proximity selection...");
          
          // Get all elements with data-id
          const elements = svgContainerRef.current.querySelectorAll('[data-id]');
          let closestElement = null;
          let closestDistance = Infinity;
          
          elements.forEach(el => {
            // Get element's bounding box
            const bbox = el.getBoundingClientRect();
            const cx = bbox.left + bbox.width / 2;
            const cy = bbox.top + bbox.height / 2;
            
            // Calculate distance from click to element center
            const clickX = e.clientX;
            const clickY = e.clientY;
            const distance = Math.sqrt(
              Math.pow(clickX - cx, 2) + Math.pow(clickY - cy, 2)
            );
            
            // If this is the closest element so far, remember it
            if (distance < closestDistance) {
              closestDistance = distance;
              closestElement = el;
            }
          });
          
          // If we found a close element and it's within a reasonable distance
          if (closestElement && closestDistance < 50) {
            const elementId = closestElement.getAttribute('data-id');
            console.log("Selected nearby element:", elementId);
            if (elementId) {
              setSelectedElement(elementId);
              setShowInspector(true);
            }
          }
        }
      }
    } else if (editMode === "add") {
      const coords = getSvgCoordinates(e);
      if (coords) {
        addNewElement(coords.x, coords.y);
      }
    }
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!selectedElement || editMode !== "select" || !svgContainerRef.current) return;

    let target = e.target as Element;
    let found = false;
    
    // Check if the clicked element is the selected one
    while (target && !found && target !== svgContainerRef.current) {
      const dataId = target.getAttribute('data-id');
      if (dataId === selectedElement) {
        found = true;
        break;
      }
      if (!target.parentElement) break;
      target = target.parentElement;
    }
    
    if (!found) return;

    const coords = getSvgCoordinates(e);
    if (!coords) return;

    setDragging(true);
    setDragStart(coords);
    e.preventDefault();
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!dragging || !dragStart || !selectedElement || !localFloorPlanData) return;

    const coords = getSvgCoordinates(e);
    if (!coords) return;

    const deltaX = coords.x - dragStart.x;
    const deltaY = coords.y - dragStart.y;

    const updatedElements = localFloorPlanData.elements.map(element => {
      if (element.id === selectedElement) {
        if (element.position) {
          const newPos: [number, number] = [
            (element.position[0] + deltaX),
            (element.position[1] + deltaY)
          ];
          return {
            ...element,
            position: newPos
          };
        } else if (element.start && element.end) {
          const newStart: [number, number] = [
            (element.start[0] + deltaX),
            (element.start[1] + deltaY)
          ];
          const newEnd: [number, number] = [
            (element.end[0] + deltaX),
            (element.end[1] + deltaY)
          ];
          return {
            ...element,
            start: newStart,
            end: newEnd
          };
        }
      }
      return element;
    });

    setLocalFloorPlanData({
      ...localFloorPlanData,
      elements: updatedElements
    });

    setDragStart(coords);
  }

  const handleMouseUp = () => {
    if (dragging && localFloorPlanData) {
      const dslCode = generateDslCode(localFloorPlanData);

      parseFloorPlan(dslCode)
        .then(data => {
          if (data && localFloorPlanData) {
            setLocalFloorPlanData(prev => ({
              ...prev!,
              svg_url: data.svg_url
            }));
            setTimestamp(Date.now());
          }
        })
        .catch(err => console.error("Error updating floor plan after drag:", err));
    }

    setDragging(false);
    setDragStart(null);
  }

  const addNewElement = (x: number, y: number) => {
    if (!localFloorPlanData) return;

    // Use timestamp to create unique IDs
    const uniqueId = Date.now().toString();
    
    const newElement: FloorPlanElement = {
      id: `${addElementType}_${uniqueId}`,
      type: addElementType as any,
    };

    switch (addElementType) {
      case "room":
        newElement.position = [x, y];
        newElement.size = [25, 25]; // More realistic room size
        break;
      case "door":
        newElement.position = [x, y];
        newElement.width = 7;
        newElement.height = 2;
        newElement.direction = "right";
        break;
      case "window":
        newElement.position = [x, y];
        newElement.width = 4;
        newElement.height = 1;
        break;
      case "bed":
        newElement.position = [x, y];
        newElement.width = 10;
        newElement.height = 15;
        break;
      case "table":
        newElement.position = [x, y];
        newElement.width = 10;
        newElement.height = 10;
        break;
      case "chair":
        newElement.position = [x, y];
        newElement.width = 7;
        newElement.height = 7;
        break;
      case "stairs":
        newElement.position = [x, y];
        newElement.width = 10;
        newElement.height = 12;
        break;
      case "elevator":
        newElement.position = [x, y];
        newElement.width = 10;
        newElement.height = 10;
        break;
    }

    const updatedData = {
      ...localFloorPlanData,
      elements: [...localFloorPlanData.elements, newElement],
    };

    // Remember element ID for selection after update
    const elementIdToSelect = newElement.id;

    setLocalFloorPlanData(updatedData);
    const dslCode = generateDslCode(updatedData);

    parseFloorPlan(dslCode)
      .then(data => {
        if (data) {
          setLocalFloorPlanData(prev => {
            if (prev) {
              return {
                ...prev,
                svg_url: data.svg_url
              };
            }
            return data;
          });
          setTimestamp(Date.now());
          
          // Select the new element after SVG is updated
          setTimeout(() => {
            setSelectedElement(elementIdToSelect);
            setShowInspector(true);
          }, 300);
        }
      })
      .catch(err => console.error("Error updating floor plan after adding element:", err));

    // Switch to select mode
    setEditMode("select");
  }

  const handleDeleteElement = () => {
    if (!localFloorPlanData || !selectedElement) return;

    const updatedElements = localFloorPlanData.elements.filter((element) => element.id !== selectedElement);

    const updatedData = {
      ...localFloorPlanData,
      elements: updatedElements,
    };

    setLocalFloorPlanData(updatedData);
    setSelectedElement(null);
    setShowInspector(false);
    
    const dslCode = generateDslCode(updatedData);
    parseFloorPlan(dslCode)
      .then(data => {
        if (data && localFloorPlanData) {
          setLocalFloorPlanData(prev => {
            if (prev) {
              return {
                ...prev,
                svg_url: data.svg_url
              };
            }
            return data;
          });
          setTimestamp(Date.now());
        }
      })
      .catch(err => console.error("Error updating floor plan after deletion:", err));
  }

  // Handle changes to form values (not actual data yet)
  const handleFormValueChange = (property: string, value: any) => {
    if (!formValues) return;
    
    if (property.includes(".")) {
      const [mainProp, index] = property.split(".");
      
      setFormValues(prev => {
        const newState = { ...prev };
        
        // Create the array if it doesn't exist
        if (!newState[mainProp]) {
          newState[mainProp] = [];
        }
        
        // Create a copy of the array
        const arr = [...newState[mainProp]];
        
        // Handle numeric validation
        const numValue = value === "" || isNaN(Number(value)) ? 0 : Number.parseFloat(value);
        arr[Number.parseInt(index)] = numValue;
        
        // Update the property
        newState[mainProp] = arr;
        return newState;
      });
    } else if (property === "width" || property === "height") {
      // Validate numeric properties - use 1 as fallback for empty values
      const numValue = value === "" || isNaN(Number(value)) ? 1 : Number.parseFloat(value);
      setFormValues(prev => ({
        ...prev,
        [property]: numValue
      }));
    } else {
      setFormValues(prev => ({
        ...prev,
        [property]: value
      }));
    }
  }
  
  // Apply changes from form to actual data
  const applyFormChanges = () => {
    if (!localFloorPlanData || !selectedElement || !formValues) return;
    
    // Check if ID has changed
    const oldId = selectedElement;
    const newId = formValues.id;
    const idHasChanged = newId !== oldId;
    
    // Update elements array with form values
    const updatedElements = localFloorPlanData.elements.map(element => {
      if (element.id === oldId) {
        return { ...formValues };
      }
      return element;
    });
    
    const updatedData = {
      ...localFloorPlanData,
      elements: updatedElements
    };
    
    // Update local floor plan data
    setLocalFloorPlanData(updatedData);
    
    // If ID changed, update selected element
    if (idHasChanged) {
      setSelectedElement(newId);
    }
    
    // Generate DSL code and update
    const dslCode = generateDslCode(updatedData);
    parseFloorPlan(dslCode)
      .then(data => {
        if (data) {
          setLocalFloorPlanData(prev => {
            if (prev) {
              return {
                ...prev,
                svg_url: data.svg_url
              };
            }
            return data;
          });
          setTimestamp(Date.now());
        }
      })
      .catch(err => console.error("Error applying form changes:", err));
  }

  const getSelectedElementDetails = () => {
    if (!formValues) return null;
    return formValues;
  }

  const renderElementProperties = () => {
    const element = getSelectedElementDetails();
    if (!element) return null;

    return (
      <div className="mt-4 space-y-4">
        <h3 className="text-sm font-medium tracking-wider text-gray-500 uppercase">Properties</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <label className="text-xs font-medium text-gray-700">ID</label>
            <Input
              value={element.id || ""}
              onChange={(e) => handleFormValueChange("id", e.target.value)}
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
                  onChange={(e) => handleFormValueChange("position.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Position Y</label>
                <Input
                  type="number"
                  value={element.position[1]}
                  onChange={(e) => handleFormValueChange("position.1", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Width</label>
                <Input
                  type="number"
                  value={element.size[0]}
                  onChange={(e) => handleFormValueChange("size.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Height</label>
                <Input
                  type="number"
                  value={element.size[1]}
                  onChange={(e) => handleFormValueChange("size.1", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="col-span-2 space-y-1">
                <label className="text-xs font-medium text-gray-700">Label</label>
                <Input
                  value={element.label || ""}
                  onChange={(e) => handleFormValueChange("label", e.target.value)}
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
                  onChange={(e) => handleFormValueChange("start.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Start Y</label>
                <Input
                  type="number"
                  value={element.start[1]}
                  onChange={(e) => handleFormValueChange("start.1", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">End X</label>
                <Input
                  type="number"
                  value={element.end[0]}
                  onChange={(e) => handleFormValueChange("end.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">End Y</label>
                <Input
                  type="number"
                  value={element.end[1]}
                  onChange={(e) => handleFormValueChange("end.1", e.target.value)}
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
                  onChange={(e) => handleFormValueChange("position.0", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Position Y</label>
                <Input
                  type="number"
                  value={element.position[1]}
                  onChange={(e) => handleFormValueChange("position.1", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Width</label>
                <Input
                  type="number"
                  value={element.width || 1}
                  onChange={(e) => handleFormValueChange("width", e.target.value)}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-700">Height</label>
                <Input
                  type="number"
                  value={element.height || 1}
                  onChange={(e) => handleFormValueChange("height", e.target.value)}
                  className="h-8"
                />
              </div>

              {element.type === "door" && (
                <div className="col-span-2 space-y-1">
                  <label className="text-xs font-medium text-gray-700">Direction</label>
                  <Select
                    value={element.direction || "right"}
                    onValueChange={(value) => handleFormValueChange("direction", value)}
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
        <div className="flex flex-col gap-2 mt-2">
          <Button variant="destructive" size="sm" onClick={handleDeleteElement}>
            <Trash2 className="w-4 h-4 mr-2" />
            Delete Element
          </Button>
          <Button variant="default" size="sm" onClick={applyFormChanges} className="text-white bg-green-600 hover:bg-green-700">
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>
    );
  }

  const handleZoomIn = () => {
    setScale((prev) => prev * 1.2);
  }

  const handleZoomOut = () => {
    setScale((prev) => prev / 1.2);
  }

  const handleResetZoom = () => {
    setScale(1);
  }

  const handleSaveChanges = async () => {
    if (!localFloorPlanData) return;

    // Apply form changes first if there are any
    if (formValues && selectedElement) {
      applyFormChanges();
    }

    const dslCode = generateDslCode(localFloorPlanData);

    try {
      const updatedData = await parseFloorPlan(dslCode);
      onUpdate(updatedData);

      setLocalFloorPlanData(updatedData);
      setTimestamp(Date.now());
    } catch (error) {
      console.error("Error saving changes:", error);
      alert("Error saving changes. Please check the console for details.");
    }
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
          if (element.width !== undefined) code += `    width: ${element.width};\n`;
          if (element.height !== undefined) code += `    height: ${element.height};\n`;
          if (element.direction) code += `    direction: "${element.direction}";\n`;
          code += `}\n\n`;
          break;
        case "window":
          code += `Window {\n`;
          code += `    id: "${element.id}";\n`;
          if (element.position) {
            code += `    position: [${element.position[0]}, ${element.position[1]}];\n`;
          }
          if (element.width !== undefined) code += `    width: ${element.width};\n`;
          if (element.height !== undefined) code += `    height: ${element.height};\n`;
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
          if (element.width !== undefined) code += `    width: ${element.width};\n`;
          if (element.height !== undefined) code += `    height: ${element.height};\n`;
          code += `}\n\n`;
          break;
      }
    });

    return code;
  };

  function downloadSvg() {
    if (!svgContent) return;
    const blob = new Blob([svgContent], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "floorplan.svg";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
  
  function downloadPng() {
    if (!svgContent) return;
    const svg = new Blob([svgContent], { type: "image/svg+xml" });
    const url = URL.createObjectURL(svg);
    const img = new window.Image();
    img.onload = function () {
      const canvas = document.createElement("canvas");
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.drawImage(img, 0, 0);
        canvas.toBlob(function (blob) {
          if (blob) {
            const a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = "floorplan.png";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(a.href);
          }
        }, "image/png");
      }
      URL.revokeObjectURL(url);
    };
    img.src = url;
  }

  return (
    <div className="relative">
      {!localFloorPlanData ? (
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
          <p className="text-center text-gray-500">Parse your DSL code to use the editor</p>
          <p className="mt-1 text-sm text-center text-gray-400">Click the "Parse & Render" button to start editing</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-1">
          <div className="bg-white border rounded-md">
            <div className="flex items-center justify-between p-2 border-b">
              <div className="flex gap-2">
                <Button
                  variant={editMode === "select" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setEditMode("select")}
                  className="h-8"
                >
                  <MousePointer className="w-4 h-4 mr-1" />
                  Select
                </Button>
                <Button
                  variant={editMode === "add" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setEditMode("add")}
                  className="h-8"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleSaveChanges}
                  className="h-8 bg-green-600 hover:bg-green-700"
                >
                  <Save className="w-4 h-4 mr-1" />
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
                    {/* Wall option removed */}
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
                <Button variant="outline" size="icon" onClick={handleZoomIn} className="w-8 h-8">
                  <ZoomIn className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="icon" onClick={handleZoomOut} className="w-8 h-8">
                  <ZoomOut className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="icon" onClick={handleResetZoom} className="w-8 h-8">
                  <Maximize className="w-4 h-4" />
                </Button>
                <Select onValueChange={(v) => v === "svg" ? downloadSvg() : downloadPng()}>
                  <SelectTrigger className="flex items-center justify-center w-12 h-8 bg-white border rounded-lg">
                    <Download className="w-8 h-8" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="svg">Download as SVG</SelectItem>
                    <SelectItem value="png">Download as PNG</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div
              className="min-h-[450px] h-[450px] overflow-auto"
              ref={svgContainerRef}
              onClick={handleSvgClick}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
            >
              {svgContent && (
                <div
                  style={{
                    transform: `scale(${scale})`,
                    transformOrigin: "top left",
                    transition: "transform 0.2s",
                    cursor: editMode === "add" ? "crosshair" : (dragging ? "grabbing" : "default")
                  }}
                  dangerouslySetInnerHTML={{ __html: svgContent }}
                />
              )}
            </div>
            {/* Side Popup Inspector */}
            {showInspector && (
              <div className="absolute right-2 top-8 z-50 w-[90vw] max-w-[260px] h-auto min-h-[320px] sm:w-[260px] sm:max-w-[260px]">
                <div className="bg-white rounded-lg shadow-lg p-4 w-full h-auto min-h-[320px] relative border flex flex-col items-stretch">
                  <button
                    className="absolute text-gray-400 top-2 right-2 hover:text-gray-700"
                    onClick={() => {
                      setSelectedElement(null);
                      setShowInspector(false);
                    }}
                  >
                    <X className="w-5 h-5" />
                  </button>
                  <h3 className="mb-4 font-medium">Element Inspector</h3>
                  {renderElementProperties()}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}