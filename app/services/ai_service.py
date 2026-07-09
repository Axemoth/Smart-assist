import json
import logging
from openai import OpenAI
from app.core.config import settings
from app.schemas.ai import AIParsedTask, AIRewrittenTask, AITaskBreakdown
from app.schemas.task import TaskPriority

logger = logging.getLogger(__name__)

# Check if the API key is set to a valid non-placeholder value
is_real_key_set = (
    settings.DEEPSEEK_API_KEY 
    and settings.DEEPSEEK_API_KEY != "your_deepseek_api_key_here"
)

# Initialize OpenAI client with DeepSeek settings
client = None
if is_real_key_set:
    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1"
    )

class AIService:
    def parse_raw_task(self, text_prompt: str) -> AIParsedTask:
        """
        Parses a raw natural language prompt into a structured task.
        """
        if not is_real_key_set:
            logger.warning("DeepSeek API Key is a placeholder. Using mock parser fallback.")
            return self._mock_parse_raw_task(text_prompt)

        try:
            response = client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI task parser. Parse the user's input string into a structured JSON task. "
                            "You must return a JSON object with the keys 'title', 'description', and 'priority'.\n"
                            "Rules:\n"
                            "1. 'priority' must be one of: 'high', 'medium', 'low'.\n"
                            "2. Infer the priority based on the urgency/deadlines mentioned.\n"
                            "3. Keep the title concise and the description clear.\n"
                            "Example output:\n"
                            "{\"title\": \"Call Mom\", \"description\": \"Ask about dinner plans for tomorrow\", \"priority\": \"medium\"}"
                        )
                    },
                    {"role": "user", "content": text_prompt}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return AIParsedTask(
                title=data.get("title", text_prompt[:50]),
                description=data.get("description", text_prompt),
                priority=TaskPriority(data.get("priority", "medium").lower())
            )
        except Exception as e:
            logger.error(f"DeepSeek parse error: {e}. Falling back to basic mapping.")
            return AIParsedTask(title=text_prompt[:50], description=text_prompt, priority=TaskPriority.MEDIUM)

    def rewrite_task(self, title: str, description: str) -> AIRewrittenTask:
        """
        Rewrites a messy task title/description into a professional, action-oriented task.
        """
        if not is_real_key_set:
            logger.warning("DeepSeek API Key is a placeholder. Using mock rewriter fallback.")
            return self._mock_rewrite_task(title, description)

        try:
            response = client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional task organizer. The user will provide a messy task. "
                            "Rewrite it into a well-mannered, highly professional, clean task.\n"
                            "You must return a JSON object with 'title', 'description', and 'priority' (must be one of: 'high', 'medium', 'low').\n"
                            "Rules:\n"
                            "1. Make the title concise but action-oriented (e.g. starting with verbs like Prepare, Clean, Organize, Resolve).\n"
                            "2. Expand the description to be detailed, clear, structured, and polite.\n"
                            "3. Set priority according to task nature (e.g., bills/taxes/critical fixes = high, casual = low).\n"
                            "Example output:\n"
                            "{\"title\": \"Organize Storage Locker\", \"description\": \"Clear out the clutter from the hallway storage locker and donate items that are no longer needed.\", \"priority\": \"low\"}"
                        )
                    },
                    {"role": "user", "content": f"Title: {title}\nDescription: {description}"}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return AIRewrittenTask(
                title=data.get("title", title),
                description=data.get("description", description),
                priority=TaskPriority(data.get("priority", "medium").lower())
            )
        except Exception as e:
            logger.error(f"DeepSeek rewrite error: {e}. Returning original.")
            return AIRewrittenTask(title=title, description=description, priority=TaskPriority.MEDIUM)

    def breakdown_task(self, title: str, description: str) -> AITaskBreakdown:
        """
        Decomposes a task into a step-by-step checklist.
        """
        if not is_real_key_set:
            logger.warning("DeepSeek API Key is a placeholder. Using mock breakdown fallback.")
            return self._mock_breakdown_task(title, description)

        try:
            response = client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a task decomposition assistant. Break down the user's task into a list of 3-7 clear, actionable subtask checklist items.\n"
                            "You must return a JSON object containing a single key 'subtasks' which maps to a list of strings.\n"
                            "Rules:\n"
                            "1. Subtasks must be short, actionable checklist actions.\n"
                            "2. Order them chronologically or logically.\n"
                            "Example output:\n"
                            "{\"subtasks\": [\"Gather travel documents\", \"Book flight tickets\", \"Pack luggage\", \"Set out-of-office autoreply\"]}"
                        )
                    },
                    {"role": "user", "content": f"Task Title: {title}\nDescription: {description}"}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return AITaskBreakdown(subtasks=data.get("subtasks", []))
        except Exception as e:
            logger.error(f"DeepSeek breakdown error: {e}.")
            return AITaskBreakdown(subtasks=["Check requirements", "Execute task", "Verify completed results"])

    # --- MOCK FALLBACKS ---
    def _mock_parse_raw_task(self, text_prompt: str) -> AIParsedTask:
        # Simplistic parsing simulation
        words = text_prompt.lower()
        priority = TaskPriority.MEDIUM
        if any(w in words for w in ["urgent", "asap", "important", "now"]):
            priority = TaskPriority.HIGH
        elif any(w in words for w in ["later", "maybe", "casual", "whenever"]):
            priority = TaskPriority.LOW
            
        title = text_prompt.split("by")[0].strip().capitalize()
        if len(title) > 60:
            title = title[:57] + "..."
            
        return AIParsedTask(
            title=f"[AI Mock] {title}",
            description=f"AI parsed from user input: '{text_prompt}'",
            priority=priority
        )

    def _mock_rewrite_task(self, title: str, description: str) -> AIRewrittenTask:
        return AIRewrittenTask(
            title=f"[AI Mock] Professionalized: {title.strip().title()}",
            description=f"This task has been rewritten for optimal clarity:\n- Action item: {description or 'Perform initial planning.'}\n- Please track progress daily.",
            priority=TaskPriority.HIGH
        )

    def _mock_breakdown_task(self, title: str, description: str) -> AITaskBreakdown:
        return AITaskBreakdown(
            subtasks=[
                f"Step 1: Setup and research for '{title}'",
                f"Step 2: Execute core development/work",
                f"Step 3: Verification, double-check checklist items",
                f"Step 4: Mark '{title}' as complete"
            ]
        )
