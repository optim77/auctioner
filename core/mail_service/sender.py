from attr import dataclass


@dataclass
class MailData:
    user_id: str
    email: str
    listing_id: str
    listing_name: str
    auction_id: str

def send_payment_mail(mail_data: MailData):
    pass