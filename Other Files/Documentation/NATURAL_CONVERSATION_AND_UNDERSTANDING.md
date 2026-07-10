# Natural Conversation and Understanding

Version 9 replaces rigid one-turn behavior with a bilingual conversation controller.

## Behaviors

- understands greetings, thanks, corrections, feelings, confusion, capability questions, and ordinary conversation
- resolves follow-ups such as “explain more,” “make it simpler,” “another example,” “use an analogy,” “why,” “how,” and “quiz me”
- carries the earlier topic into the next request
- changes the explanation method when the learner is confused
- asks the local generator to answer the user’s intent rather than echo the prompt
- removes common canned introductions and duplicate lines
- preserves exact mathematical, command, and code outputs
- supports English and Greek

Small models still have limited language capacity. The conversation layer improves context, prompting, retrieval, fallback answers, and cleanup; it does not change the model’s parameter count.
