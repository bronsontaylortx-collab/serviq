import os
import copy
import json
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL", "").strip()
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if not database_url:
    raise RuntimeError("DATABASE_URL is not set. Add it to your local .env file or Render environment variables.")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class QAOverride(db.Model):
    __tablename__ = "qa_overrides"

    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.String(100), nullable=False, index=True)
    question_name = db.Column(db.String(200), nullable=False, index=True)
    ai_result = db.Column(db.String(50), nullable=True)
    ai_confidence = db.Column(db.Integer, nullable=True)
    human_result = db.Column(db.String(50), nullable=False)
    override_reason = db.Column(db.Text, nullable=True)
    reviewer = db.Column(db.String(200), nullable=False, default="Bronson Taylor")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


with app.app_context():
    db.create_all()

# =========================================================

# DASHBOARD ANALYZER SCORECARD

# =========================================================

QUESTIONS = [

    {"id": "auth", "name": "Authentication", "points": 20, "critical": True},

    {"id": "discovery", "name": "Discovery", "points": 15, "critical": False},

    {"id": "empathy", "name": "Empathy", "points": 15, "critical": False},

    {"id": "resolution", "name": "Resolution / Next Step", "points": 25, "critical": False},

    {"id": "communication", "name": "Professional Communication", "points": 10, "critical": False},

    {"id": "closing", "name": "Closing / Expectations", "points": 15, "critical": False},

]

DEMO = """Agent [00:00]: Thank you for calling mortgage servicing. My name is Jordan. May I have your name and verify the required account information?

Borrower [00:09]: This is Alex. I completed the verification. I am calling because I lost my job last month and I cannot make the full mortgage payment.

Agent [00:22]: I see the payment is past due. How much are you able to pay today?

Borrower [00:33]: That is why I am calling. I am worried about losing the house and I need to know if there is any help available.

Agent [00:45]: I can review the available assistance path and explain the next steps. I will first confirm some information about your hardship.

Agent [01:02]: After we review that information, I will let you know the next step and what documents may be needed. Is there anything else you need help with today?"""

# =========================================================

# DEMO CALL DATA

# Later this will come from the database / RingCX

# =========================================================

CALLS = {

    "bronson-001": {

        "id": "bronson-001",

        "agent": "Bronson Taylor",

        "initials": "BT",

        "department": "Loss Mitigation",

        "duration": "9:14",

        "time": "Today 1:36 PM",

        "score": 97,

        "status": "PASS",

        "confidence": 98,

        "total_points": "87 / 90",

        "pass_rate": "100%",

        "needs_review": 0,

        "critical_findings": 0,

        "summary": (

            "Borrower contacted mortgage servicing after a reduction in income. "

            "Bronson completed authentication, identified the hardship, acknowledged "

            "the borrower's concern, reviewed available assistance options and clearly "

            "explained the next steps."

        ),

        "scorecard": [

            {

                "name": "Authentication",

                "points": "20 / 20",

                "result": "PASS",

                "confidence": 99,

                "critical": True,

                "reason": "Required authentication was completed before account-specific servicing information was discussed.",

                "timestamp": "00:04",

                "evidence": "Before we discuss the account, I need to complete verification with you."

            },

            {

                "name": "Discovery",

                "points": "15 / 15",

                "result": "PASS",

                "confidence": 98,

                "critical": False,

                "reason": "The reason for the call and the borrower's financial hardship were clearly identified.",

                "timestamp": "00:31",

                "evidence": "So your income was reduced this month and you're concerned about making the full payment, correct?"

            },

            {

                "name": "Empathy",

                "points": "15 / 15",

                "result": "PASS",

                "confidence": 97,

                "critical": False,

                "reason": "The borrower received a direct and appropriate acknowledgement of the hardship.",

                "timestamp": "00:48",

                "evidence": "I understand why that would be stressful, and I'll go through the available options with you."

            },

            {

                "name": "Resolution / Next Step",

                "points": "25 / 25",

                "result": "PASS",

                "confidence": 99,

                "critical": False,

                "reason": "Available assistance and the next required actions were clearly explained.",

                "timestamp": "01:18",

                "evidence": "I'll review the assistance options with you and explain exactly what we need for the next step."

            },

            {

                "name": "Professional Communication",

                "points": "7 / 10",

                "result": "PASS",

                "confidence": 94,

                "critical": False,

                "reason": "Communication remained professional and easy to understand throughout the interaction.",

                "timestamp": "02:10",

                "evidence": "I'll walk through each option so you know what to expect."

            },

            {

                "name": "Closing / Expectations",

                "points": "5 / 5",

                "result": "PASS",

                "confidence": 98,

                "critical": False,

                "reason": "The borrower was given clear expectations before the call ended.",

                "timestamp": "08:51",

                "evidence": "You should receive the document request, and if you have questions you can contact us again."

            }

        ],

        "transcript": [

            {

                "time": "00:04",

                "speaker": "AGENT",

                "text": "Before we discuss the account, I need to complete verification with you."

            },

            {

                "time": "00:16",

                "speaker": "BORROWER",

                "text": "Okay, that's fine."

            },

            {

                "time": "00:31",

                "speaker": "AGENT",

                "text": "So your income was reduced this month and you're concerned about making the full payment, correct?"

            },

            {

                "time": "00:39",

                "speaker": "BORROWER",

                "text": "Yes. My hours were cut and I'm worried about getting behind."

            },

            {

                "time": "00:48",

                "speaker": "AGENT",

                "text": "I understand why that would be stressful, and I'll go through the available options with you."

            },

            {

                "time": "01:18",

                "speaker": "AGENT",

                "text": "I'll review the assistance options with you and explain exactly what we need for the next step."

            },

            {

                "time": "08:51",

                "speaker": "AGENT",

                "text": "You should receive the document request, and if you have questions you can contact us again."

            }

        ]

    },

    "jordan-001": {

        "id": "jordan-001",

        "agent": "Jordan Miller",

        "initials": "JM",

        "department": "Loss Mitigation",

        "duration": "8:42",

        "time": "Today 12:48 PM",

        "score": 94,

        "status": "PASS",

        "confidence": 96,

        "total_points": "69 / 90",

        "pass_rate": "83%",

        "needs_review": 1,

        "critical_findings": 0,

        "summary": (

            "Borrower called due to recent job loss and inability to make the full "

            "mortgage payment. Jordan completed authentication, gathered hardship "

            "information and explained an assistance path. Empathy was identified "

            "as the primary coaching opportunity."

        ),

        "scorecard": [

            {

                "name": "Authentication",

                "points": "20 / 20",

                "result": "PASS",

                "confidence": 98,

                "critical": True,

                "reason": "Required authentication language was detected before account-specific servicing discussion.",

                "timestamp": "00:00",

                "evidence": "May I have your name and verify the required account information?"

            },

            {

                "name": "Discovery",

                "points": "15 / 15",

                "result": "PASS",

                "confidence": 96,

                "critical": False,

                "reason": "The borrower clearly explained the reason for the call and the hardship situation.",

                "timestamp": "00:09",

                "evidence": "I lost my job last month and I cannot make the full mortgage payment."

            },

            {

                "name": "Empathy",

                "points": "9 / 15",

                "result": "PARTIAL",

                "confidence": 88,

                "critical": False,

                "reason": "The borrower expressed concern about losing the home, but the emotional concern was not explicitly acknowledged.",

                "timestamp": "00:33",

                "evidence": "I am worried about losing the house and I need to know if there is any help available."

            },

            {

                "name": "Resolution / Next Step",

                "points": "25 / 25",

                "result": "PASS",

                "confidence": 97,

                "critical": False,

                "reason": "The agent explained a clear assistance path and identified the next steps.",

                "timestamp": "00:45",

                "evidence": "I can review the available assistance path and explain the next steps."

            }

        ],

        "transcript": [

            {

                "time": "00:00",

                "speaker": "AGENT",

                "text": "Thank you for calling mortgage servicing. My name is Jordan. May I have your name and verify the required account information?"

            },

            {

                "time": "00:09",

                "speaker": "BORROWER",

                "text": "This is Alex. I completed the verification. I am calling because I lost my job last month and I cannot make the full mortgage payment."

            },

            {

                "time": "00:22",

                "speaker": "AGENT",

                "text": "I see the payment is past due. How much are you able to pay today?"

            },

            {

                "time": "00:33",

                "speaker": "BORROWER",

                "text": "I am worried about losing the house and I need to know if there is any help available."

            },

            {

                "time": "00:45",

                "speaker": "AGENT",

                "text": "I can review the available assistance path and explain the next steps."

            }

        ]

    },

    "ashley-001": {

        "id": "ashley-001",

        "agent": "Ashley Reed",

        "initials": "AR",

        "department": "Payment",

        "duration": "6:17",

        "time": "Today 11:32 AM",

        "score": 88,

        "status": "HUMAN REVIEW",

        "confidence": 84,

        "total_points": "79 / 90",

        "pass_rate": "83%",

        "needs_review": 2,

        "critical_findings": 0,

        "summary": (

            "Borrower contacted servicing regarding a payment concern. Ashley "

            "completed the core servicing steps, but ServIQ detected lower confidence "

            "around empathy and closing expectations. Human review is recommended."

        ),

        "scorecard": [

            {

                "name": "Authentication",

                "points": "20 / 20",

                "result": "PASS",

                "confidence": 97,

                "critical": True,

                "reason": "Authentication was completed before account details were discussed.",

                "timestamp": "00:05",

                "evidence": "Let me verify the account before we review the payment."

            },

            {

                "name": "Discovery",

                "points": "15 / 15",

                "result": "PASS",

                "confidence": 94,

                "critical": False,

                "reason": "The payment issue was clearly identified.",

                "timestamp": "00:29",

                "evidence": "You're calling because the payment has not posted yet, correct?"

            },

            {

                "name": "Empathy",

                "points": "10 / 15",

                "result": "PARTIAL",

                "confidence": 84,

                "critical": False,

                "reason": "ServIQ detected possible acknowledgement, but confidence is below the automatic decision threshold.",

                "timestamp": "00:52",

                "evidence": "I can see why you'd want to get that corrected."

            },

            {

                "name": "Resolution / Next Step",

                "points": "25 / 25",

                "result": "PASS",

                "confidence": 95,

                "critical": False,

                "reason": "The payment research process and next step were explained.",

                "timestamp": "01:14",

                "evidence": "I'll submit the payment research request and explain what happens next."

            }

        ],

        "transcript": [

            {

                "time": "00:05",

                "speaker": "AGENT",

                "text": "Let me verify the account before we review the payment."

            },

            {

                "time": "00:21",

                "speaker": "BORROWER",

                "text": "My payment came out of my bank account but it still isn't showing."

            },

            {

                "time": "00:29",

                "speaker": "AGENT",

                "text": "You're calling because the payment has not posted yet, correct?"

            },

            {

                "time": "00:52",

                "speaker": "AGENT",

                "text": "I can see why you'd want to get that corrected."

            },

            {

                "time": "01:14",

                "speaker": "AGENT",

                "text": "I'll submit the payment research request and explain what happens next."

            }

        ]

    },

    "david-001": {

        "id": "david-001",

        "agent": "David Torres",

        "initials": "DT",

        "department": "Delinquency",

        "duration": "11:03",

        "time": "Today 10:16 AM",

        "score": 72,

        "status": "CRITICAL FAILURE",

        "confidence": 97,

        "total_points": "65 / 90",

        "pass_rate": "67%",

        "needs_review": 1,

        "critical_findings": 1,

        "summary": (

            "The delinquency discussion contained a critical authentication finding. "

            "ServIQ detected account-specific servicing discussion before sufficient "

            "verification evidence was present. Supervisor review is required."

        ),

        "scorecard": [

            {

                "name": "Authentication",

                "points": "0 / 20",

                "result": "FAIL",

                "confidence": 99,

                "critical": True,

                "reason": "Account-specific delinquency information appears to have been discussed before required authentication was completed.",

                "timestamp": "00:08",

                "evidence": "I can see you're two payments behind on the mortgage."

            },

            {

                "name": "Discovery",

                "points": "15 / 15",

                "result": "PASS",

                "confidence": 96,

                "critical": False,

                "reason": "The reason for the delinquency was identified.",

                "timestamp": "00:44",

                "evidence": "So the missed payments started after your medical leave?"

            },

            {

                "name": "Empathy",

                "points": "15 / 15",

                "result": "PASS",

                "confidence": 94,

                "critical": False,

                "reason": "The hardship was appropriately acknowledged.",

                "timestamp": "01:03",

                "evidence": "I'm sorry you've been dealing with that."

            },

            {

                "name": "Resolution / Next Step",

                "points": "25 / 25",

                "result": "PASS",

                "confidence": 97,

                "critical": False,

                "reason": "The next servicing action was clearly explained.",

                "timestamp": "01:35",

                "evidence": "The next step is to review the available assistance options."

            }

        ],

        "transcript": [

            {

                "time": "00:08",

                "speaker": "AGENT",

                "text": "I can see you're two payments behind on the mortgage."

            },

            {

                "time": "00:19",

                "speaker": "BORROWER",

                "text": "Yes, I've been trying to get caught up."

            },

            {

                "time": "00:44",

                "speaker": "AGENT",

                "text": "So the missed payments started after your medical leave?"

            },

            {

                "time": "01:03",

                "speaker": "AGENT",

                "text": "I'm sorry you've been dealing with that."

            },

            {

                "time": "01:35",

                "speaker": "AGENT",

                "text": "The next step is to review the available assistance options."

            }

        ]

    },

    "sarah-001": {

        "id": "sarah-001",

        "agent": "Sarah Kim",

        "initials": "SK",

        "department": "Escrow",

        "duration": "5:54",

        "time": "Yesterday 4:42 PM",

        "score": 97,

        "status": "PASS",

        "confidence": 98,

        "total_points": "87 / 90",

        "pass_rate": "100%",

        "needs_review": 0,

        "critical_findings": 0,

        "summary": (

            "The borrower contacted servicing regarding an escrow payment increase. "

            "Sarah authenticated the borrower, identified the concern, explained the "

            "escrow analysis and clearly set expectations for the next statement."

        ),

        "scorecard": [

            {

                "name": "Authentication",

                "points": "20 / 20",

                "result": "PASS",

                "confidence": 99,

                "critical": True,

                "reason": "Required verification was completed.",

                "timestamp": "00:03",

                "evidence": "Before I access the escrow details, let's complete verification."

            },

            {

                "name": "Discovery",

                "points": "15 / 15",

                "result": "PASS",

                "confidence": 98,

                "critical": False,

                "reason": "The escrow concern was clearly identified.",

                "timestamp": "00:35",

                "evidence": "You're calling because the monthly payment increased after the escrow analysis."

            },

            {

                "name": "Empathy",

                "points": "15 / 15",

                "result": "PASS",

                "confidence": 96,

                "critical": False,

                "reason": "The agent appropriately acknowledged the payment concern.",

                "timestamp": "00:48",

                "evidence": "I understand an unexpected increase can be frustrating."

            },

            {

                "name": "Resolution / Next Step",

                "points": "25 / 25",

                "result": "PASS",

                "confidence": 99,

                "critical": False,

                "reason": "The escrow analysis and future payment expectations were clearly explained.",

                "timestamp": "01:16",

                "evidence": "I'll explain what changed in the analysis and what your payment will be going forward."

            }

        ],

        "transcript": [

            {

                "time": "00:03",

                "speaker": "AGENT",

                "text": "Before I access the escrow details, let's complete verification."

            },

            {

                "time": "00:25",

                "speaker": "BORROWER",

                "text": "I don't understand why my payment went up."

            },

            {

                "time": "00:35",

                "speaker": "AGENT",

                "text": "You're calling because the monthly payment increased after the escrow analysis."

            },

            {

                "time": "00:48",

                "speaker": "AGENT",

                "text": "I understand an unexpected increase can be frustrating."

            },

            {

                "time": "01:16",

                "speaker": "AGENT",

                "text": "I'll explain what changed in the analysis and what your payment will be going forward."

            }

        ]

    }

}

# =========================================================

# DASHBOARD DEMO ANALYZER

# =========================================================

def evaluate(text):
    """Extract transcript facts with AI, then apply ServIQ grading rules in Python."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    # The model extracts narrow, observable facts. Python—not the model—decides
    # PASS / PARTIAL / FAIL / N/A and calculates the score.
    fact_names = [
        "auth_completed_before_account_info",
        "account_info_disclosed",
        "reason_for_call_identified",
        "material_need_or_hardship_identified",
        "agent_explored_or_confirmed_relevant_details",
        "meaningful_concern_or_hardship_expressed",
        "agent_directly_acknowledged_concern",
        "agent_indirectly_acknowledged_concern",
        "clear_concrete_next_step",
        "vague_or_incomplete_next_step",
        "communication_clear_respectful_professional",
        "material_communication_problem",
        "interaction_includes_ending",
        "expectations_or_followup_set",
        "closing_or_additional_help_check",
    ]

    schema = {
        "type": "object",
        "properties": {
            "facts": {
                "type": "array",
                "minItems": len(fact_names),
                "maxItems": len(fact_names),
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "enum": fact_names},
                        "value": {"type": "boolean"},
                        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
                        "evidence": {"type": "string"},
                        "timestamp": {"type": "string"},
                    },
                    "required": ["name", "value", "confidence", "evidence", "timestamp"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["facts"],
        "additionalProperties": False,
    }

    instructions = """
You are the evidence-extraction layer for ServIQ. This development version uses synthetic mortgage-servicing transcripts only.

Your ONLY job is to extract the listed observable facts. Do NOT grade the call. Do NOT output PASS, PARTIAL, FAIL, N/A, points, or an overall score.

STRICT EXTRACTION RULES:
1. Use only the supplied transcript. Never assume an action happened off transcript.
2. A fact is TRUE only when the transcript contains affirmative evidence for it. Ambiguous or missing evidence = FALSE.
3. Evidence must be a short EXACT excerpt copied from the transcript. Never paraphrase it.
4. For a FALSE fact, evidence may quote the strongest contrary/relevant excerpt; otherwise use an empty string.
5. Timestamp must match the quoted evidence. If there is no evidence, use an empty string.
6. Confidence means confidence that the TRUE/FALSE extraction is correct.
7. Return every fact exactly once.

FACT DEFINITIONS:
- auth_completed_before_account_info: TRUE only if the transcript explicitly establishes completed verification/authentication before any account-specific servicing information is disclosed. Asking to verify is not completion. A customer statement such as "I completed the verification" can establish completion if it occurs before account-specific disclosure.
- account_info_disclosed: TRUE if the agent states account-specific information such as delinquency, payment status, balance, escrow/account details, or similar protected servicing information.
- reason_for_call_identified: TRUE if the transcript establishes why the customer contacted the company or what issue they need addressed.
- material_need_or_hardship_identified: TRUE if the relevant servicing need, hardship, or material problem is stated or confirmed.
- agent_explored_or_confirmed_relevant_details: TRUE only if the AGENT asks about, confirms, summarizes, or otherwise develops relevant details beyond merely hearing the initial problem statement.
- meaningful_concern_or_hardship_expressed: TRUE if the customer expresses worry, fear, frustration, hardship, loss, confusion, distress, or a similarly meaningful concern.
- agent_directly_acknowledged_concern: TRUE only if the AGENT explicitly acknowledges the customer's emotional concern/hardship (for example, stressful, frustrating, difficult, sorry, understand your concern). Offering a solution alone is not acknowledgement.
- agent_indirectly_acknowledged_concern: TRUE if the agent gives some human acknowledgement of the situation but does not clearly/directly acknowledge the expressed emotional concern. Do not mark TRUE merely because the agent offers a solution.
- clear_concrete_next_step: TRUE only if the transcript shows a concrete next action or resolution that is already established for this interaction. A promise to review something later, explain steps later, or "let you know" the next step later is NOT concrete.
- vague_or_incomplete_next_step: TRUE when a future path, review, possible documents/options, or later explanation is mentioned but the actual next action remains unresolved or conditional. For "I can review..." / "After we review... I will let you know the next step..." set this TRUE and clear_concrete_next_step FALSE.
- communication_clear_respectful_professional: TRUE if the agent language shown is understandable, respectful, and professional with no material problem.
- material_communication_problem: TRUE only if the transcript contains a material clarity, tone, misleading, disrespectful, confusing, or professionalism problem.
- interaction_includes_ending: TRUE if the transcript includes the natural end/closing portion of the interaction, not merely an excerpt that stops mid-process.
- expectations_or_followup_set: TRUE if the agent sets concrete expectations about timing, documents, follow-up, what happens next, or another relevant post-call expectation.
- closing_or_additional_help_check: TRUE if the agent performs a clear closing behavior such as asking whether anything else is needed or otherwise clearly closes the interaction.

Before returning, re-check each TRUE value against its exact definition. When uncertain, use FALSE.
"""

    response = client.responses.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-6-luna"),
        instructions=instructions,
        input=text,
        text={
            "format": {
                "type": "json_schema",
                "name": "serviq_fact_extraction",
                "strict": True,
                "schema": schema,
            }
        },
    )

    payload = json.loads(response.output_text)
    facts = {item["name"]: item for item in payload.get("facts", [])}

    missing = [name for name in fact_names if name not in facts]
    if missing:
        raise RuntimeError(f"AI response missing facts: {', '.join(missing)}")

    def is_true(name):
        return bool(facts[name]["value"])

    def choose_evidence(*names):
        for name in names:
            item = facts[name]
            if item.get("evidence"):
                return item["evidence"], item.get("timestamp", "")
        return "", ""

    def confidence_for(*names):
        values = [int(facts[name]["confidence"]) for name in names]
        return min(values) if values else 100

    decisions = {}

    # Authentication: deterministic critical sequencing rule.
    if is_true("auth_completed_before_account_info"):
        result = "PASS"
        reason = "The transcript establishes completed authentication before account-specific servicing information was disclosed."
        evidence, timestamp = choose_evidence("auth_completed_before_account_info")
    else:
        result = "FAIL"
        reason = "The transcript does not establish completed authentication before account-specific servicing information was disclosed."
        evidence, timestamp = choose_evidence("account_info_disclosed", "auth_completed_before_account_info")
    decisions["auth"] = (result, confidence_for("auth_completed_before_account_info", "account_info_disclosed"), reason, evidence, timestamp)

    # Discovery: reason + material need + agent development = PASS.
    discovery_core = is_true("reason_for_call_identified") and is_true("material_need_or_hardship_identified")
    discovery_developed = is_true("agent_explored_or_confirmed_relevant_details")
    if discovery_core and discovery_developed:
        result = "PASS"
        reason = "The reason for the call and material servicing need were identified, and the agent developed or confirmed relevant details."
    elif discovery_core:
        result = "PARTIAL"
        reason = "The reason for the call and material need were identified, but the agent did not sufficiently develop or confirm relevant details."
    else:
        result = "FAIL"
        reason = "The transcript does not establish sufficient discovery of the reason for the call and material servicing need."
    evidence, timestamp = choose_evidence("agent_explored_or_confirmed_relevant_details", "material_need_or_hardship_identified", "reason_for_call_identified")
    decisions["discovery"] = (result, confidence_for("reason_for_call_identified", "material_need_or_hardship_identified", "agent_explored_or_confirmed_relevant_details"), reason, evidence, timestamp)

    # Empathy: only applicable when a meaningful concern/hardship exists.
    if not is_true("meaningful_concern_or_hardship_expressed"):
        result = "N/A"
        reason = "The transcript does not contain a meaningful concern or hardship requiring an empathy response."
    elif is_true("agent_directly_acknowledged_concern"):
        result = "PASS"
        reason = "The agent directly acknowledged the customer's expressed concern or hardship."
    elif is_true("agent_indirectly_acknowledged_concern"):
        result = "PARTIAL"
        reason = "The agent provided some acknowledgement, but it did not fully or directly address the expressed concern."
    else:
        result = "FAIL"
        reason = "A meaningful concern or hardship was expressed, but the agent did not acknowledge it."
    evidence, timestamp = choose_evidence("agent_directly_acknowledged_concern", "agent_indirectly_acknowledged_concern", "meaningful_concern_or_hardship_expressed")
    decisions["empathy"] = (result, confidence_for("meaningful_concern_or_hardship_expressed", "agent_directly_acknowledged_concern", "agent_indirectly_acknowledged_concern"), reason, evidence, timestamp)

    # Resolution / next step.
    if is_true("vague_or_incomplete_next_step"):
        result = "PARTIAL"
        reason = "The agent mentioned a future path or action, but the next step remained vague or incomplete."
    elif is_true("clear_concrete_next_step"):
        result = "PASS"
        reason = "The agent mentioned a future path or action, but the next step remained vague or incomplete."
    else:
        result = "FAIL"
        reason = "The transcript does not contain a meaningful resolution or next step."
    evidence, timestamp = choose_evidence("clear_concrete_next_step", "vague_or_incomplete_next_step")
    decisions["resolution"] = (result, confidence_for("clear_concrete_next_step", "vague_or_incomplete_next_step"), reason, evidence, timestamp)

    # Professional communication.
    if is_true("material_communication_problem"):
        result = "FAIL"
        reason = "The transcript contains a material communication or professionalism problem."
    elif is_true("communication_clear_respectful_professional"):
        result = "PASS"
        reason = "The agent's communication was clear, respectful, understandable, and professional."
    else:
        result = "PARTIAL"
        reason = "Communication was not shown to have a major failure, but the transcript does not fully support the PASS standard."
    evidence, timestamp = choose_evidence("material_communication_problem", "communication_clear_respectful_professional")
    decisions["communication"] = (result, confidence_for("communication_clear_respectful_professional", "material_communication_problem"), reason, evidence, timestamp)

    # Closing / expectations.
    if not is_true("interaction_includes_ending"):
        result = "N/A"
        reason = "The transcript does not clearly include the end of the interaction, so closing cannot be fairly evaluated."
    elif is_true("expectations_or_followup_set") and is_true("closing_or_additional_help_check"):
        result = "PASS"
        reason = "The agent set relevant expectations and performed a clear closing behavior."
    elif is_true("expectations_or_followup_set") or is_true("closing_or_additional_help_check"):
        result = "PARTIAL"
        reason = "Some closing or expectation-setting was present, but the close was incomplete."
    else:
        result = "FAIL"
        reason = "The interaction ended without meaningful closing or expectation-setting."
    evidence, timestamp = choose_evidence("expectations_or_followup_set", "closing_or_additional_help_check", "interaction_includes_ending")
    decisions["closing"] = (result, confidence_for("interaction_includes_ending", "expectations_or_followup_set", "closing_or_additional_help_check"), reason, evidence, timestamp)

    results = []
    total_awarded = 0
    total_possible = 0

    for q in QUESTIONS:
        result, confidence, reason, evidence, timestamp = decisions[q["id"]]

        if result == "N/A":
            awarded, possible = 0, 0
        elif result == "PASS":
            awarded, possible = q["points"], q["points"]
        elif result == "PARTIAL":
            awarded, possible = round(q["points"] / 2), q["points"]
        else:
            awarded, possible = 0, q["points"]

        total_awarded += awarded
        total_possible += possible

        results.append({
            **q,
            "result": result,
            "awarded": awarded,
            "confidence": confidence,
            "why": reason,
            "reason": reason,
            "evidence": evidence,
            "timestamp": timestamp,
            "review": result == "PARTIAL" or confidence < 90,
        })

    score = round((total_awarded / total_possible) * 100) if total_possible else 0
    return score, results


# =========================================================
# ROUTES
# =========================================================

@app.route("/", methods=["GET", "POST"])

def home():

    transcript = DEMO

    result = None

    if request.method == "POST":

        transcript = request.form.get("transcript", "").strip()

        if transcript:

            score, items = evaluate(transcript)

            result = {

                "score": score,

                "items": items,

                "review_count": sum(1 for x in items if x["review"]),

                "critical": any(

                    x["critical"] and x["result"] == "FAIL"

                    for x in items

                ),

            }

    return render_template(

        "index.html",

        transcript=transcript,

        result=result,

    )

@app.route("/calls")

def calls():

    return render_template("calls.html")

# Keep the old URL working.

@app.route("/review", methods=["GET", "POST"])

def review_default():

    return review_call("jordan-001")

# Dynamic review page.

@app.route("/review/<call_id>", methods=["GET", "POST"])
def review_call(call_id):
    source_call = CALLS.get(call_id)

    if not source_call:
        abort(404)

    # Work on a copy so human review never overwrites the original AI demo data.
    call = copy.deepcopy(source_call)

    override_saved = False
    human_result = None
    override_reason = ""
    question_name = ""

    if request.method == "POST":
        human_result = request.form.get("human_result", "").strip().upper()
        override_reason = request.form.get("override_reason", "").strip()
        question_name = request.form.get("question_name", "").strip()

        valid_results = {"PASS", "FAIL", "PARTIAL", "N/A"}
        scorecard_item = next(
            (item for item in source_call.get("scorecard", []) if item.get("name") == question_name),
            None,
        )

        if human_result in valid_results and question_name and scorecard_item:
            override = QAOverride(
                call_id=call_id,
                question_name=question_name,
                ai_result=scorecard_item.get("result"),
                ai_confidence=scorecard_item.get("confidence"),
                human_result=human_result,
                override_reason=override_reason or None,
                reviewer="Bronson Taylor",
            )
            db.session.add(override)
            db.session.commit()
            override_saved = True

    override_records = (
        QAOverride.query
        .filter_by(call_id=call_id)
        .order_by(QAOverride.created_at.desc(), QAOverride.id.desc())
        .all()
    )

    override_history = [
        {
            "id": item.id,
            "question_name": item.question_name,
            "ai_result": item.ai_result,
            "ai_confidence": item.ai_confidence,
            "human_result": item.human_result,
            "override_reason": item.override_reason or "",
            "reviewer": item.reviewer,
            "created_at": item.created_at,
        }
        for item in override_records
    ]

    # The first record for each question is the newest because the query is DESC.
    latest_overrides = {}
    for item in override_records:
        if item.question_name not in latest_overrides:
            latest_overrides[item.question_name] = {
                "human_result": item.human_result,
                "override_reason": item.override_reason or "",
                "reviewer": item.reviewer,
                "created_at": item.created_at,
            }

    # Apply the latest human decision to the working copy of the scorecard.
    # Keep the original AI values on each item so the UI can show an audit trail.
    awarded_total = 0
    possible_total = 0
    applicable_items = 0
    passed_items = 0
    needs_review = 0
    critical_findings = 0

    for item in call.get("scorecard", []):
        original_result = item.get("result", "")
        original_points = item.get("points", "0 / 0")

        try:
            awarded_text, possible_text = [part.strip() for part in original_points.split("/", 1)]
            original_awarded = int(awarded_text)
            max_points = int(possible_text)
        except (ValueError, AttributeError):
            original_awarded = 0
            max_points = 0

        item["ai_result"] = original_result
        item["ai_points"] = original_points
        item["ai_confidence"] = item.get("confidence")
        item["human_override"] = False
        item["override_reason"] = ""
        item["reviewer"] = ""
        item["override_created_at"] = None

        latest = latest_overrides.get(item.get("name"))
        effective_result = original_result
        effective_awarded = original_awarded

        if latest:
            effective_result = latest["human_result"]
            item["human_override"] = True
            item["override_reason"] = latest["override_reason"]
            item["reviewer"] = latest["reviewer"]
            item["override_created_at"] = latest["created_at"]

            if effective_result == "PASS":
                effective_awarded = max_points
            elif effective_result == "FAIL":
                effective_awarded = 0
            elif effective_result == "PARTIAL":
                # Preserve an existing partial award; otherwise use half credit.
                if original_result == "PARTIAL":
                    effective_awarded = original_awarded
                else:
                    effective_awarded = round(max_points / 2)
            elif effective_result == "N/A":
                effective_awarded = 0

        item["result"] = effective_result
        item["points"] = (
            "N/A" if effective_result == "N/A"
            else f"{effective_awarded} / {max_points}"
        )

        if effective_result != "N/A":
            applicable_items += 1
            possible_total += max_points
            awarded_total += effective_awarded

            if effective_result == "PASS":
                passed_items += 1

            # A human-reviewed item is considered resolved even when AI confidence was low.
            if not item["human_override"] and (
                effective_result == "PARTIAL" or item.get("confidence", 100) < 90
            ):
                needs_review += 1

            if item.get("critical") and effective_result == "FAIL":
                critical_findings += 1

    call["score"] = round((awarded_total / possible_total) * 100) if possible_total else 0
    call["total_points"] = f"{awarded_total} / {possible_total}"
    call["pass_rate"] = (
        f"{round((passed_items / applicable_items) * 100)}%"
        if applicable_items else "0%"
    )
    call["needs_review"] = needs_review
    call["critical_findings"] = critical_findings

    if critical_findings:
        call["status"] = "CRITICAL FAILURE"
    elif needs_review:
        call["status"] = "HUMAN REVIEW"
    else:
        call["status"] = "PASS"

    if request.method == "GET" and override_records:
        latest = override_records[0]
        human_result = latest.human_result
        override_reason = latest.override_reason or ""
        question_name = latest.question_name

    return render_template(
        "review.html",
        call=call,
        override_saved=override_saved,
        human_result=human_result,
        override_reason=override_reason,
        question_name=question_name,
        override_history=override_history,
        latest_overrides=latest_overrides,
    )

@app.route("/analytics")

def analytics():

    return render_template("analytics.html")

if __name__ == "__main__":

    app.run(debug=True, port=5000)
