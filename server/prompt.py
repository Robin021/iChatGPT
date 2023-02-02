

class Prompt:
    """
    Prompt class with methods to construct prompt
    """

    def __init__(self) -> None:
        """
        Initialize prompt with base prompt
        """
        self.base_prompt = ( "You are ChatGPT, a large language model trained by OpenAI. You answer as concisely as possible for each response (e.g. Don't be verbose).\n"
        )
        # Track chat history
        self.chat_history: list = []

    def add_to_chat_history(self, chat: str) -> None:
        """
        Add chat to chat history for next prompt
        """
        self.chat_history.append(chat)

    def history(self) -> str:
        """
        Return chat history
        """
        return "\n\n\n\n".join(self.chat_history)

    def construct_prompt(self, new_prompt: str) -> str:
        """
        Construct prompt based on chat history and request
        """
        prompt = (
            self.base_prompt + self.history() + "You: " + new_prompt + "\nChatGPT:"
        )
        # Check if prompt over 4000*4 characters
        if len(prompt) > 4000 * 4:
            # Remove oldest chat
            self.chat_history.pop(0)
            # Construct prompt again
            prompt = self.construct_prompt(new_prompt)
        return prompt
