from anthropic import Anthropic


class ReviewsAggregator:
    def __init__(
        self, client: Anthropic | None = None, model: str = "claude-haiku-4-5"
    ):
        self.client = client
        self.model = model

    def summarize_reviews(self, reviews: list[dict], max_reviews: int = 10) -> str:
        reviews_text = "\n\n".join(
            [
                f"{review['author']}: {review['content']}"
                for review in reviews[:max_reviews]
            ]
        )
        prompt = f"""You are a movie review aggregator. Analyze the following reviews and provide a structured summary. 
                    Reviews:
                    {reviews_text}

                    Respond in this exact format:
                    PROS:
                    - [main advantage]: [brief explanation]
                    - [main advantage]: [brief explanation]
                    - [main advantage]: [brief explanation]

                    CONS:
                    - [main drawback]: [brief explanation]
                    - [main drawback]: [brief explanation]
                    - [main drawback]: [brief explanation]

                    OVERALL:
                    Score: [X]/10
                    Audience: [who would enjoy this film and why, 2-3 sentences max]

                    Keep each point concise. Maximum 3 pros and 3 cons."""

        if self.client is None:
            raise ValueError("Anthropic client not provided for ReviewsAggregator.")
        message = self.client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model,
        )
        return next(
            block for block in message.content if block.type == "text"
        ).text.strip()
