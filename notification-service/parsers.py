from notification_events import OutbidPayload, OutbidDTO

def parse_outbid_event(data: dict) -> OutbidDTO:
    payload = data["payload"]
    print(payload)
    return OutbidDTO(
        event_type=data["event_type"],
        payload=OutbidPayload(
            auction_id=payload["auction_id"],
            receiver_id=payload["receiver_id"],
            listing_id=payload["listing_id"],
            listing_name=payload["listing_name"],
            bid_price=payload["bid_price"],
        ),
    )