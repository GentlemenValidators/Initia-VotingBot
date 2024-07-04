import requests
import json
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = ''  # Replace with your actual bot token
CHECK_INTERVAL = 60  # Interval to check for new proposals in seconds

def load_chain_endpoints(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def fetch_active_governance_proposals(chain, endpoint):
    url = f"{endpoint}/cosmos/gov/v1/proposals?proposal_status=2"
    try:
        response = requests.get(url)
        if response.status_code == 404:  # Skip if endpoint not found
            return None
        if response.status_code == 501:  # Skip if endpoint does not support the functionality
            print(f"Endpoint not implemented for {chain}")
            return None
        response.raise_for_status()
        data = response.json()
        return data.get("proposals", [])
    except requests.RequestException as e:
        print(f"Error fetching active proposals for {chain}: {e}")
        return None

def generate_mintscan_link(chain, proposal_id):
    return f"https://scan.testnet.initia.xyz/initiation-1/proposals/{proposal_id}"

def check_for_new_proposals(context: CallbackContext):
    chain_endpoints = load_chain_endpoints("chains.json")
    new_messages = []
    known_proposals = context.job.context["known_proposals"]

    for chain, endpoint in chain_endpoints.items():
        proposals = fetch_active_governance_proposals(chain, endpoint)
        if proposals:
            for proposal in proposals:
                proposal_id = proposal.get('id', 'No ID available')
                if proposal_id not in known_proposals:
                    title = proposal.get('title', 'No title available')
                    mintscan_link = generate_mintscan_link(chain, proposal_id)
                    message = f"*New Governance Proposal for {chain.title()}:*\n Proposal ID: {proposal_id}\n Title: {title}\n Details: {mintscan_link}\n"
                    new_messages.append(message)
                    known_proposals.add(proposal_id)

    if new_messages:
        full_message = "\n".join(new_messages)
        context.bot.send_message(chat_id=context.job.context["chat_id"], text=full_message, parse_mode='Markdown')

def start(update: Update, context: CallbackContext) -> None:
    # Initialize known proposals
    known_proposals = set()
    chain_endpoints = load_chain_endpoints("chains.json")

    for chain, endpoint in chain_endpoints.items():
        proposals = fetch_active_governance_proposals(chain, endpoint)
        if proposals:
            for proposal in proposals:
                known_proposals.add(proposal.get('id', 'No ID available'))

    # Send initial message with current proposals
    full_message = main()
    context.bot.send_message(chat_id=update.effective_chat.id, text=full_message, parse_mode='Markdown')

    # Start job to check for new proposals
    context.job_queue.run_repeating(check_for_new_proposals, interval=CHECK_INTERVAL, first=0, context={
        "chat_id": update.effective_chat.id,
        "known_proposals": known_proposals
    })

def main():
    chain_endpoints = load_chain_endpoints("chains.json")
    messages = []

    for chain, endpoint in chain_endpoints.items():
        proposals = fetch_active_governance_proposals(chain, endpoint)
        if proposals:
            message = f"*Active Governance Proposals for {chain.title()}:*\n"
            for proposal in proposals:
                title = proposal.get('title', 'No title available')
                proposal_id = proposal.get('id', 'No ID available')
                mintscan_link = generate_mintscan_link(chain, proposal_id)
                message += f" Proposal ID: {proposal_id}\n Title: {title}\n Details: {mintscan_link}\n"
            messages.append(message)

    # Combine all messages and return, or return a default message if empty
    full_message = "\n".join(messages) if messages else "No active governance proposals found."
    return full_message

if __name__ == "__main__":
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()
