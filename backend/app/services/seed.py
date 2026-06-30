from sqlmodel import Session, select

from app.models import RoundRobinState, Seller

SELLER_QUEUE: tuple[str, ...] = (
    "Marcelo",
    "Rafael",
    "Renato",
    "Pedro",
    "Leonardo",
)

ROUND_ROBIN_STATE_ID = 1


def seed_initial_data(session: Session) -> None:
    for queue_order, seller_name in enumerate(SELLER_QUEUE, start=1):
        seller = session.exec(select(Seller).where(Seller.name == seller_name)).one_or_none()

        if seller is None:
            session.add(Seller(name=seller_name, queue_order=queue_order))
        elif seller.queue_order != queue_order:
            seller.queue_order = queue_order
            session.add(seller)

    state = session.get(RoundRobinState, ROUND_ROBIN_STATE_ID)
    if state is None:
        session.add(
            RoundRobinState(
                id=ROUND_ROBIN_STATE_ID,
                next_seller_order=1,
            )
        )

    session.commit()

