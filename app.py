from flask import Flask, render_template, request, abort

app = Flask(__name__)


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
    low = text.lower()
    results = []

    auth = "verify" in low or "verification" in low

    hardship = any(x in low for x in [
        "lost my job",
        "hardship",
        "cannot make",
        "can't make",
        "worried",
        "losing the house",
    ])

    empathy = any(x in low for x in [
        "sorry to hear",
        "understand how",
        "i understand",
        "sorry you're",
        "sorry you",
    ])

    resolution = any(x in low for x in [
        "next step",
        "assistance",
        "documents may be needed",
        "review the available",
    ])

    closing = any(x in low for x in [
        "anything else",
        "next step",
        "what happens next",
    ])

    configs = [
        (
            "auth",
            auth,
            0.98,
            "Authentication language was found."
            if auth else
            "No clear authentication evidence was found.",
        ),
        (
            "discovery",
            True,
            0.92,
            "The borrower clearly states the reason for the call.",
        ),
        (
            "empathy",
            empathy if hardship else True,
            0.96 if hardship else 0.80,
            "A hardship/empathy trigger is present and explicit acknowledgement was found."
            if empathy else
            "A hardship/empathy trigger is present, but no explicit acknowledgement was found.",
        ),
        (
            "resolution",
            resolution,
            0.93,
            "A resolution path or actionable next step was found."
            if resolution else
            "No clear resolution or next step was found.",
        ),
        (
            "communication",
            True,
            0.89,
            "No obvious unprofessional language was detected in this prototype.",
        ),
        (
            "closing",
            closing,
            0.86,
            "Closing/expectation language was found."
            if closing else
            "No clear closing expectations were found.",
        ),
    ]

    total = 0

    for qid, passed, conf, why in configs:
        q = next(q for q in QUESTIONS if q["id"] == qid)

        pts = q["points"] if passed else 0
        total += pts

        review = conf < 0.90

        results.append({
            **q,
            "result": "PASS" if passed else "FAIL",
            "awarded": pts,
            "confidence": round(conf * 100),
            "why": why,
            "review": review,
        })

    return round(total), results


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

    call = CALLS.get(call_id)

    if not call:
        abort(404)

    override_saved = False
    human_result = None
    override_reason = ""
    question_name = ""

    if request.method == "POST":

        human_result = request.form.get(
            "human_result", ""
        ).strip()

        override_reason = request.form.get(
            "override_reason", ""
        ).strip()

        question_name = request.form.get(
            "question_name", ""
        ).strip()

        if human_result and question_name:
            override_saved = True

    return render_template(
        "review.html",
        call=call,
        override_saved=override_saved,
        human_result=human_result,
        override_reason=override_reason,
        question_name=question_name,
    )

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")
if __name__ == "__main__":
    app.run(debug=True, port=5000)
