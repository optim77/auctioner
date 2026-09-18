from notification_events import OutbidDTO

def handle_outbid_event(e: OutbidDTO):
    print(
        f"User {e.payload.receiver_id} "
        f"was outbid on {e.payload.listing_name}. "
        f"Current price: {e.payload.bid_price}"
    )




