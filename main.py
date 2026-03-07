"""Main entry point for AI Research WhatsApp Digest."""

import os
import sys

from dotenv import load_dotenv

from src.research_fetcher import fetch_ai_research
from src.news_ranker import rank_research
from src.news_summarizer import summarize_research, summarize_research_detailed
from src.whatsapp_sender import format_research_message, send_whatsapp_message
from src.pdf_generator import generate_research_pdf


def main():
    """Fetch AI research, select the most important, and send to WhatsApp."""
    # Load environment variables
    load_dotenv()

    # Get required environment variables
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
    your_whatsapp = os.getenv("YOUR_WHATSAPP_NUMBER")
    openai_key = os.getenv("OPENAI_API_KEY")

    # Validate required variables
    missing = []
    if not twilio_sid:
        missing.append("TWILIO_ACCOUNT_SID")
    if not twilio_token:
        missing.append("TWILIO_AUTH_TOKEN")
    if not twilio_whatsapp:
        missing.append("TWILIO_WHATSAPP_NUMBER")
    if not your_whatsapp:
        missing.append("YOUR_WHATSAPP_NUMBER")
    if not openai_key:
        missing.append("OPENAI_API_KEY")

    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    # Fetch AI research
    print("Fetching AI research...")
    research_items = []
    try:
        research_items = fetch_ai_research(max_results=10)
        print(f"Found {len(research_items)} research items")
    except Exception as e:
        print(f"Error fetching research: {e}")

    # Check if we have any content
    if not research_items:
        print("No AI research found today")
        sys.exit(0)

    # Rank and select top research
    print("Selecting most important research...")
    try:
        top_research = rank_research(research_items, openai_key)
        print(f"Selected: {top_research['title']}")
    except Exception as e:
        print(f"Error ranking research: {e}")
        top_research = research_items[0]

    # Generate short summary for WhatsApp
    print("Generating WhatsApp summary...")
    try:
        top_research = summarize_research(top_research, openai_key)
        if "summary" in top_research:
            print("Generated short summary for WhatsApp")
    except Exception:
        print("Warning: Could not generate WhatsApp summary")

    # Generate detailed summary for PDF
    print("Generating detailed PDF summary...")
    try:
        top_research = summarize_research_detailed(top_research, openai_key)
        if "detailed_summary" in top_research:
            print("Generated detailed summary for PDF")
    except Exception:
        print("Warning: Could not generate detailed summary")

    # Generate PDF report
    print("Generating PDF report...")
    try:
        pdf_path = generate_research_pdf(top_research)
        print(f"PDF saved: {pdf_path}")
    except Exception:
        print("Warning: Could not generate PDF")

    # Send WhatsApp message
    print("Sending WhatsApp message...")
    try:
        message = format_research_message(top_research)
        message_sid = send_whatsapp_message(
            twilio_sid,
            twilio_token,
            twilio_whatsapp,
            your_whatsapp,
            message,
        )
        print(f"Message sent successfully! SID: {message_sid}")
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
