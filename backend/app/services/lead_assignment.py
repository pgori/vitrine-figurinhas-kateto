from sqlalchemy import text
from sqlmodel import Session, select

from app.models import KANBAN_COLUMN_NO_CONTACT, Lead, RoundRobinState, Seller
from app.models.base import utc_now
from app.schemas import LeadCreate
from app.services.seed import ROUND_ROBIN_STATE_ID


def create_lead_with_round_robin(session: Session, lead_data: LeadCreate) -> Lead:
    _begin_assignment_transaction(session)

    try:
        state = _get_round_robin_state_for_update(session)
        assigned_seller = _get_next_seller(session, state.next_seller_order)

        lead = Lead(
            name=lead_data.name,
            desired_item=lead_data.desired_item,
            phone=lead_data.phone,
            kanban_column=KANBAN_COLUMN_NO_CONTACT,
            assigned_seller_id=assigned_seller.id,
        )

        state.next_seller_order = _get_following_seller_order(
            session,
            current_order=assigned_seller.queue_order,
        )
        state.updated_at = utc_now()

        session.add(lead)
        session.add(state)
        session.commit()
        return lead
    except Exception:
        session.rollback()
        raise


def _begin_assignment_transaction(session: Session) -> None:
    if session.in_transaction():
        raise RuntimeError("A distribuicao round robin deve iniciar sem transacao ativa.")

    dialect_name = session.get_bind().dialect.name
    if dialect_name == "sqlite":
        session.exec(text("BEGIN IMMEDIATE"))
        return

    session.begin()


def _get_round_robin_state_for_update(session: Session) -> RoundRobinState:
    statement = (
        select(RoundRobinState)
        .where(RoundRobinState.id == ROUND_ROBIN_STATE_ID)
        .with_for_update()
    )
    state = session.exec(statement).one_or_none()

    if state is None:
        raise RuntimeError("Estado do round robin nao foi inicializado.")

    return state


def _get_next_seller(session: Session, queue_order: int) -> Seller:
    seller = session.exec(
        select(Seller).where(Seller.queue_order == queue_order)
    ).one_or_none()

    if seller is None or seller.id is None:
        raise RuntimeError("Fila de vendedores inconsistente para o round robin.")

    return seller


def _get_following_seller_order(session: Session, current_order: int) -> int:
    following_order = session.exec(
        select(Seller.queue_order)
        .where(Seller.queue_order > current_order)
        .order_by(Seller.queue_order)
        .limit(1)
    ).one_or_none()

    if following_order is not None:
        return following_order

    first_order = session.exec(
        select(Seller.queue_order).order_by(Seller.queue_order).limit(1)
    ).one()
    return first_order
