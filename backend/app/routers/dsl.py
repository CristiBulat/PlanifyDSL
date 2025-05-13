from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi import Depends
import os
import xml.etree.ElementTree as ET
import re

from .. import schemas
from ..database import get_db
from ..services.dsl_service import DSLService
from ..config import SVG_OUTPUT_DIR

router = APIRouter(
    prefix="/api",
    tags=["dsl"],
    responses={404: {"description": "Not found"}},
)

# Initialize the DSL service
dsl_service = DSLService()


def enhance_svg_with_element_ids(svg_path, elements):
    """
    Add data-id attributes to SVG elements for editor interaction

    Args:
        svg_path: Path to the SVG file
        elements: List of floor plan elements

    Returns:
        bool: Success status
    """
    try:
        # Parse the SVG file
        # Use a namespace mapping to properly handle SVG elements
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        # First, register the namespaces with ElementTree
        ET.register_namespace('', namespaces['svg'])

        # Read the file content
        with open(svg_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already enhanced
        if 'data-id=' in content:
            return True

        # Parse the XML
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()

        # Create a mapping of elements by ID and type
        elements_by_id = {}
        elements_by_type = {}

        for element in elements:
            element_id = element.get('id')
            element_type = element.get('type')

            if element_id:
                elements_by_id[element_id] = element

            if element_type:
                if element_type not in elements_by_type:
                    elements_by_type[element_type] = []
                elements_by_type[element_type].append(element)

        # Process room elements (typically represented as rectangles or paths)
        room_elements = []
        for elem in root.findall('.//svg:rect', namespaces) + root.findall('.//svg:path', namespaces):
            room_elements.append(elem)

        # Match room elements with their data
        if 'room' in elements_by_type and room_elements:
            rooms = elements_by_type['room']
            for i, room_data in enumerate(rooms):
                if i < len(room_elements):
                    room_id = room_data.get('id', f'room_{i}')
                    room_elements[i].set('data-id', room_id)
                    room_elements[i].set('data-type', 'room')

        # Process wall elements (typically lines)
        wall_elements = root.findall('.//svg:line', namespaces)
        if 'wall' in elements_by_type and wall_elements:
            walls = elements_by_type['wall']
            for i, wall_data in enumerate(walls):
                if i < len(wall_elements):
                    wall_id = wall_data.get('id', f'wall_{i}')
                    wall_elements[i].set('data-id', wall_id)
                    wall_elements[i].set('data-type', 'wall')

        # Process door elements
        door_elements = []
        for elem in root.findall('.//svg:path', namespaces):
            if 'M' in elem.get('d', ''):  # Simple check for path data that might be a door arc
                door_elements.append(elem)

        if 'door' in elements_by_type and door_elements:
            doors = elements_by_type['door']
            for i, door_data in enumerate(doors):
                if i < len(door_elements):
                    door_id = door_data.get('id', f'door_{i}')
                    door_elements[i].set('data-id', door_id)
                    door_elements[i].set('data-type', 'door')

        # Process window elements
        window_elements = []
        for elem in root.findall('.//svg:rect', namespaces):
            fill = elem.get('fill', '')
            if 'E6F7FF' in fill:  # Light blue typically used for windows
                window_elements.append(elem)

        if 'window' in elements_by_type and window_elements:
            windows = elements_by_type['window']
            for i, window_data in enumerate(windows):
                if i < len(window_elements):
                    window_id = window_data.get('id', f'window_{i}')
                    window_elements[i].set('data-id', window_id)
                    window_elements[i].set('data-type', 'window')

        # Process furniture elements
        furniture_types = ['bed', 'table', 'chair', 'stairs', 'elevator']
        for furniture_type in furniture_types:
            if furniture_type in elements_by_type:
                # Look for groups, rectangles, or specific furniture patterns
                furniture_elements = root.findall('.//svg:g', namespaces)
                if not furniture_elements:
                    furniture_elements = root.findall('.//svg:rect', namespaces)

                furniture_items = elements_by_type[furniture_type]
                for i, furniture_data in enumerate(furniture_items):
                    if i < len(furniture_elements):
                        furniture_id = furniture_data.get('id', f'{furniture_type}_{i}')
                        furniture_elements[i].set('data-id', furniture_id)
                        furniture_elements[i].set('data-type', furniture_type)

        # Write the enhanced SVG back to file
        tree.write(svg_path, encoding='utf-8', xml_declaration=True)

        return True

    except Exception as e:
        print(f"Error enhancing SVG with element IDs: {e}")
        # Return True anyway to not block the process
        return True


@router.post("/parse", response_model=schemas.FloorPlanResponse)
async def parse_dsl_code(
        request: schemas.DSLCodeRequest,
        db: Session = Depends(get_db)
):
    """
    Parse DSL code and return a floor plan
    """
    try:
        # Process the DSL code
        user_id = str(request.user_id) if request.user_id else None
        elements, svg_path = dsl_service.process_dsl_code(request.code, user_id)

        # Enhance the SVG with element IDs for editor interaction
        enhance_svg_with_element_ids(svg_path, elements)

        # Create relative URL for the SVG file
        svg_filename = os.path.basename(svg_path)
        svg_url = f"/api/svg/{svg_filename}"

        # Debug output
        print(f"SVG URL: {svg_url}")

        # Return the response
        response_data = {
            "elements": elements,
            "svg_url": svg_url
        }
        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/svg/{filename}")
async def get_svg(filename: str):
    """
    Serve the generated SVG file
    """
    svg_path = os.path.join(SVG_OUTPUT_DIR, filename)

    if not os.path.exists(svg_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SVG file not found"
        )

    return FileResponse(
        svg_path,
        media_type="image/svg+xml",
        filename=filename
    )