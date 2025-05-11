from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi import Depends
import os

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