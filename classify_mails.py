from typesafe_sdk import Choice, TypeSafeClient
from dotenv import load_dotenv
from pull_emails import pull_mails, get_gmail_service
from label_emails import apply_labels_to_email

load_dotenv()

# Initialize the TypeSafe client
client = TypeSafeClient()

# Mock data representing Gmail content
mock_emails = [
    {
        "subject": "Your HDFC Bank Statement for August",
        "body": "Dear Customer, please find attached your account statement for the month of August. Do not share your OTP or password with anyone."
    },
    {
        "subject": "Your Amazon.in order has shipped!",
        "body": "Great news! Your order for 'Wireless Noise Cancelling Headphones' has shipped and will arrive by tomorrow."
    },
    {
        "subject": "Interview Invitation: Software Engineer at TechCorp",
        "body": "Hi there, we reviewed your profile and would love to schedule a 30-minute initial call to discuss the Software Engineer position."
    },
    {
        "subject": "Top posts from Stack Overflow this week",
        "body": "Here are the top questions and answers from the Stack Overflow community this week. Check out the latest discussions on React and Python."
    },
    {
        "subject": "Your Flight Booking Confirmation: DEL to BOM",
        "body": "Thank you for booking with MakeMyTrip. Your flight ticket (PNR: XYZ123) from New Delhi to Mumbai is confirmed for the 15th of next month."
    },
    {
        "subject": "Alert: Suspicious login attempt to your banking account",
        "body": "We noticed a login attempt from a new device. If this wasn't you, please secure your banking account immediately."
    }
]

def classify_emails(mail_content, service):
    print("Starting email classification...\n")
    
    for email in mail_content:
        content_to_classify = f"Subject: {email['subject']}\nBody: {email['body']}"
        
        response = client.system_one(
            content_to_classify,
            {
                "category": Choice(
                    instructions="Classify this email into the correct category based on its content.",
                    criteria={
                        "banking": "Banking alerts, account statements, financial transactions, OTPs",
                        "ecommerce": "Order confirmations, shipping updates, product promotions, online shopping",
                        "recruitment": "Job opportunities, interview scheduling, recruiter messages",
                        "tech community": "Tech newsletters, developer forum updates, programming community discussions",
                        "travel": "Flight tickets, hotel bookings, travel itineraries, vacation planning",
                        "other": "Emails that do not fit into any of the specific categories above"
                    },
                )
            },
            model="openjev-latest",
        )
        
        predicted_category = response.choices["category"].choice
        print(f"Email Subject: {email['subject']}")
        print(f"Email body: {email['body']}")
        print(f"Classified as: {predicted_category.upper()}\n")
        
        # Apply labels to the email
        if 'id' in email and service:
            apply_labels_to_email(service, email['id'], predicted_category)
            
        print("-" * 40)

if __name__ == "__main__":
    service = get_gmail_service()
    mail_content = pull_mails(no_of_mails=1)
    
    if service and mail_content:
        classify_emails(mail_content, service)

