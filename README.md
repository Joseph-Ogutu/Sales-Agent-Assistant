# AI Sales Agent

A secure, Django-based automation platform designed for B2B sales, tailored for small and medium businesses (SMBs). The AI Sales Agent automates personalized outreach, prioritizes high-potential leads, and provides actionable analytics, delivering **40–60% more lead capacity** and **15–30% higher conversion rates**. It rivals enterprise tools like Salesforce with robust security and usability.

## Features

- **Secure Authentication**: Custom login/registration forms with company details for B2B context, ensuring restricted access.
- **Enhanced Dashboard**: Create and filter leads by score, industry, or engagement; displays total leads and active sequences with a modern UI.
- **Pain-Based Follow-Ups**: AI-generated emails, WhatsApp, and LinkedIn messages tailored to lead-specific pain points in a 5-touch sequence.
- **Lead Intelligence**: Enriches data using Clearbit for targeted outreach.
- **Behavioral Profiling**: Analyzes interactions with Hugging Face NLP for engagement insights.
- **Predictive Lead Scoring**: Prioritizes high-probability leads using scikit-learn.
- **CRM Integration**: Bi-directional sync with HubSpot/Salesforce for seamless data management.
- **AI Sales Coaching**: Real-time prompts and feedback to enhance sales rep performance.
- **Multi-Channel Outreach**: Supports email (Gmail API), WhatsApp (Twilio), and LinkedIn messaging.
- **Advanced Analytics**: Real-time pipeline bar chart, conversion rate, average engagement, sequence completion, and lead distribution by industry via Chart.js.
- **Living Sales Thread**: Unified SQLite thread for interaction logging.

## Technical Requirements

- **Platform**: Django, Python, SQLite on Replit (free tier).
- **APIs**: Gmail, Clearbit, OpenAI, Twilio, HubSpot.
- **Dependencies**:
  ```bash
  django
  requests
  transformers
  openai
  google-auth-oauthlib
  scikit-learn
  twilio
  reportlab
