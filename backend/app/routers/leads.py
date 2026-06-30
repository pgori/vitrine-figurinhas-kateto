from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Lead, Seller
from app.models.base import utc_now
from app.schemas import KanbanColumn, LeadCardRead, LeadCreate, LeadMove, SellerRead
from app.services.auth import AuthenticatedUser, get_current_user
from app.services.lead_assignment import create_lead_with_round_robin

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadCardRead, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_data: LeadCreate,
    session: Session = Depends(get_session),
) -> LeadCardRead:
    lead = create_lead_with_round_robin(session, lead_data)
    return _build_lead_card(session, lead)


@router.get("", response_model=list[LeadCardRead])
def list_leads(
    column: KanbanColumn | None = Query(default=None),
    _current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[LeadCardRead]:
    statement = select(Lead).order_by(Lead.id)

    if column is not None:
        statement = statement.where(Lead.kanban_column == column.value)

    leads = session.exec(statement).all()
    return [_build_lead_card(session, lead) for lead in leads]


@router.patch("/{lead_id}", response_model=LeadCardRead)
def move_lead(
    lead_id: int,
    lead_move: LeadMove,
    _current_user: AuthenticatedUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> LeadCardRead:
    lead = session.get(Lead, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nao encontrado.",
        )

    lead.kanban_column = lead_move.kanban_column.value
    lead.updated_at = utc_now()
    session.add(lead)
    session.commit()
    session.refresh(lead)

    return _build_lead_card(session, lead)


def _build_lead_card(session: Session, lead: Lead) -> LeadCardRead:
    if lead.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lead criado sem identificador.",
        )

    seller = session.get(Seller, lead.assigned_seller_id)
    if seller is None or seller.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vendedor atribuido nao encontrado.",
        )

    return LeadCardRead(
        id=lead.id,
        name=lead.name,
        desired_item=lead.desired_item,
        phone=lead.phone,
        kanban_column=KanbanColumn(lead.kanban_column),
        assigned_seller=SellerRead(
            id=seller.id,
            name=seller.name,
            queue_order=seller.queue_order,
        ),
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )

