from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.models import Lead, RoundRobinState, Seller
from app.schemas import LeadCreate
from app.services.lead_assignment import create_lead_with_round_robin
from app.services.seed import ROUND_ROBIN_STATE_ID, SELLER_QUEUE


def test_round_robin_order_is_circular(session: Session) -> None:
    for index in range(7):
        create_lead_with_round_robin(session, _lead_data(index))

    assert _assigned_seller_names(session) == [
        "Marcelo",
        "Rafael",
        "Renato",
        "Pedro",
        "Leonardo",
        "Marcelo",
        "Rafael",
    ]

    state = session.get(RoundRobinState, ROUND_ROBIN_STATE_ID)
    assert state is not None
    assert state.next_seller_order == 3


def test_round_robin_state_persists_after_reopening_connection(
    database_url: str,
    engine: Engine,
) -> None:
    with Session(engine, expire_on_commit=False) as first_session:
        for index in range(3):
            create_lead_with_round_robin(first_session, _lead_data(index))

    engine.dispose()

    reopened_engine = _create_sqlite_engine(database_url)
    try:
        with Session(reopened_engine, expire_on_commit=False) as reopened_session:
            create_lead_with_round_robin(reopened_session, _lead_data(3))

            assert _assigned_seller_names(reopened_session) == [
                "Marcelo",
                "Rafael",
                "Renato",
                "Pedro",
            ]

            state = reopened_session.get(RoundRobinState, ROUND_ROBIN_STATE_ID)
            assert state is not None
            assert state.next_seller_order == 5
    finally:
        reopened_engine.dispose()


def test_round_robin_does_not_skip_or_duplicate_under_concurrency(
    engine: Engine,
) -> None:
    total_leads = len(SELLER_QUEUE) * 2

    def create_concurrent_lead(index: int) -> None:
        with Session(engine, expire_on_commit=False) as concurrent_session:
            create_lead_with_round_robin(concurrent_session, _lead_data(index))

    with ThreadPoolExecutor(max_workers=total_leads) as executor:
        list(executor.map(create_concurrent_lead, range(total_leads)))

    with Session(engine, expire_on_commit=False) as verification_session:
        assert _assigned_seller_names(verification_session) == list(SELLER_QUEUE) * 2


def _lead_data(index: int) -> LeadCreate:
    return LeadCreate(
        name=f"Lead {index}",
        desired_item=f"Carta {index}",
        phone=f"119999900{index:02d}",
    )


def _assigned_seller_names(session: Session) -> list[str]:
    sellers = {
        seller.id: seller.name
        for seller in session.exec(select(Seller).order_by(Seller.queue_order)).all()
    }
    leads = session.exec(select(Lead).order_by(Lead.id)).all()
    return [sellers[lead.assigned_seller_id] for lead in leads]


def _create_sqlite_engine(database_url: str) -> Engine:
    from sqlmodel import create_engine

    return create_engine(
        database_url,
        connect_args={"check_same_thread": False, "timeout": 30},
    )

