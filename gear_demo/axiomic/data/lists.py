class ChatList:
    def __init__(self):
        self.messages = []
    
    def append(self, user_message, response):
        self.messages.append({"user": user_message, "response": response})
    
    def format(self, most_recent_user=None):
        formatted = ""
        for msg in self.messages:
            formatted += f"User: {msg['user']}\nAssistant: {msg['response']}\n\n"
        if most_recent_user:
            formatted += f"User: {most_recent_user}\n"
        return formatted
