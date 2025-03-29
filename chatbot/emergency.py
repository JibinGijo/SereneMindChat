import re

EMERGENCY_PHRASES = [
    r"kill\s*(my)?self",
    r"end\s*it\s*all",
    r"suicide",
    r"harm\s*(my)?self",
    r"don'?t\s*want\s*to\s*live",
    r"no\s*reason\s*to\s*live"
]

def check_emergency(message):
    message_lower = message.lower()
    for phrase in EMERGENCY_PHRASES:
        if re.search(phrase, message_lower):
            return {
                'is_emergency': True,
                'message': "I'm really concerned about what you're saying. Would you like me to connect you with help immediately?"
            }
    return {'is_emergency': False}