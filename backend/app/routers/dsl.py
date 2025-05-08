from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from .. import models, schemas
from ..database import get_db
from ..services.dsl_service import DSLService

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
        elements, svg_path = dsl_service.process_dsl_code(request.code)

        # Create relative URL for the SVG file
        svg_filename = os.path.basename(svg_path)
        svg_url = f"/api/svg/{svg_filename}"

        # Save to database if user_id is provided
        if request.user_id:
            # Create new floor plan in DB
            db_floor_plan = models.FloorPlan(
                title=request.title or "Untitled Floor Plan",
                description=request.description,
                dsl_code=request.code,
                svg_output=svg_path,
                user_id=request.user_id
            )
            db.add(db_floor_plan)
            db.commit()
            db.refresh(db_floor_plan)

        # Return the response
        return {
            "elements": elements,
            "svg_url": svg_url
        }

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
    svg_path = os.path.join(dsl_service._init__()[0], filename)

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


@router.get("/floor-plans", response_model=list[schemas.FloorPlan])
async def get_floor_plans(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    Get all floor plans
    """
    floor_plans = db.query(models.FloorPlan).offset(skip).limit(limit).all()
    return floor_plans


@router.get("/floor-plans/{floor_plan_id}", response_model=schemas.FloorPlan)
async def get_floor_plan(
        floor_plan_id: int,
        db: Session = Depends(get_db)
):
    """
    Get a floor plan by ID
    """
    floor_plan = db.query(models.FloorPlan).filter(models.FloorPlan.id == floor_plan_id).first()

    if not floor_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Floor plan not found"
        )

    return floor_plan