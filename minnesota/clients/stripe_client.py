"""Utils for Stripe"""

from os import environ
from datetime import datetime
from stripe._stripe_client import StripeClient

IS_TEST: bool = environ.get("IS_TEST", "false").lower().strip() == "true"


def get_stripe_client() -> StripeClient:
    """Get the stripe client"""
    if "STRIPE_API_KEY" not in environ:
        raise ValueError("STRIPE_API_KEY is not set")
    endpoint: dict[str, str] = {}
    if (
        "STRIPE_ENDPOINT_URL" in environ
        and len(environ["STRIPE_ENDPOINT_URL"].strip()) > 0
    ):
        endpoint = {
            "api": environ["STRIPE_ENDPOINT_URL"],
        }

    return StripeClient(
        environ["STRIPE_API_KEY"],
        base_addresses=endpoint,  # type: ignore[arg-type]
    )


def check_is_active(end_timestamp: int) -> bool:
    """Check if a subscription is active"""
    now: datetime
    if __debug__ and IS_TEST:  # The mock api returns 2009/2/4, 0:31:30
        now = datetime(2009, 2, 2, 6, 0, 0)  # Groundhog day
    else:
        now = datetime.now()
    return datetime.fromtimestamp(end_timestamp) > now


def check_stripe(email: str, must_be_advanced: bool) -> bool:
    """Check if a user has an active subscription"""
    client: StripeClient = get_stripe_client()
    plan: list[str] | None = None
    if must_be_advanced:
        plan = [
            pl.strip()
            for pl in environ.get("ADVANCED_PLANS", "").split(",")
            if len(pl.strip()) > 0
        ]
    try:
        customer = client.customers.list(params={"email": email}).data[0]
        subscription = client.subscriptions.list(
            params={"customer": customer.id, "status": "active"}
        ).data[0]
        product_id = subscription["items"]["data"][0]["price"]["product"]
        if must_be_advanced and plan is not None and len(plan) > 0:
            if product_id not in plan:
                return False
        return check_is_active(subscription.current_period_end)
    except (KeyError, IndexError):
        return False


__all__ = ["check_stripe", "get_stripe_client"]
