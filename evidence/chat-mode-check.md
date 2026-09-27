# Chat Mode Evidence

## Test definition

- Mode: `chat`
- Execution: local
- Model: Gemma 4 E2B IT Text int4 through MLX-VLM
- Purpose: verify ordinary conversation without forced retrieval and verify multi-turn context

## Initial run

The user first asked, “What can you help me with?” Gemma described drafting, brainstorming, summarization, organization, and conversation without producing an insufficient-evidence refusal or unrelated wiki citations. Response time: **8.09 seconds**.

The user then requested a short interview-availability email for every Friday from 2–4 p.m. in October 2026. Gemma retained that context through two corrections. It correctly identified the Friday dates as October 2, 9, 16, 23, and 30. Recorded response times were **13.51**, **3.65**, and **10.85 seconds**.

## Actual failure

The final response ended with the incomplete line:

> * **Friday, October 30, 20

The model hit the configured 320-token output limit before completing the email. It also asked for additional clarification even though the original request already provided enough information.

## Fix

- Increased the chat-only output allowance from 320 to 520 tokens. Ask mode remains at 320 tokens.
- Added an assistant rule to complete a request without unnecessary follow-up when enough information is available.
- Normalized visible escaped Markdown markers such as `\*` for cleaner terminal display.
- Added selective automatic retrieval when chat explicitly refers to “my notes,” “my wiki,” or similar phrases. Ordinary drafting still skips retrieval.

## Rerun

### Coffee-chat email run

The user requested an alumni coffee-chat email containing three details: a referral from Rachel, interest in the alumnus's Chase recruiting experience, and a flexible 15-minute conversation the following week. Gemma produced complete drafts in **14.27 seconds** without consulting the wiki.

The user then asked, “Make it sounds more natural and friendly.” Gemma retained the referral, Chase recruiting topic, 15-minute duration, and next-week timing while revising the tone. The follow-up completed in **9.01 seconds** without truncation.

Assessment: pass for ordinary chat and conversational context. Two presentation limitations remained: Gemma provided two alternatives rather than one concise default, and escaped Markdown asterisks remained visible. The assistant instruction was updated to return one strong draft by default, and terminal formatting cleanup was strengthened. A final short “Make that shorter” check remains pending because it is the specific boundary test requested by the assignment.

### Required short-follow-up run

User: `Write a two-sentence thank-you note to a mentor.`

Gemma produced two two-sentence options. Response time: **8.44 seconds**.

User: `Make that shorter.`

Gemma responded:

> “Thank you for your invaluable mentorship; I truly appreciate your guidance. I feel much better for your support.”

Response time: **2.43 seconds**.

Assessment: pass for conversation context and shortening. The second reply clearly refers to and shortens the prior draft, and neither turn requires wiki evidence. Observed model-quality limitation: “I feel much better for your support” is understandable but unnatural English, and the first turn still offered two options despite the one-draft instruction. A concrete future improvement would be a small writing-specific prompt plus a final grammar/conciseness check before display.
