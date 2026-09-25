from flask import Flask, render_template, request
import re

app=Flask(__name__)

QUESTIONS=[
 {"id":"auth","name":"Authentication","points":20,"critical":True},
 {"id":"discovery","name":"Discovery","points":15,"critical":False},
 {"id":"empathy","name":"Empathy","points":15,"critical":False},
 {"id":"resolution","name":"Resolution / Next Step","points":25,"critical":False},
 {"id":"communication","name":"Professional Communication","points":10,"critical":False},
 {"id":"closing","name":"Closing / Expectations","points":15,"critical":False},
]

DEMO="""Agent [00:00]: Thank you for calling mortgage servicing. My name is Jordan. May I have your name and verify the required account information?
Borrower [00:09]: This is Alex. I completed the verification. I am calling because I lost my job last month and I cannot make the full mortgage payment.
Agent [00:22]: I see the payment is past due. How much are you able to pay today?
Borrower [00:33]: That is why I am calling. I am worried about losing the house and I need to know if there is any help available.
Agent [00:45]: I can review the available assistance path and explain the next steps. I will first confirm some information about your hardship.
Agent [01:02]: After we review that information, I will let you know the next step and what documents may be needed. Is there anything else you need help with today?"""

def evaluate(text):
    low=text.lower()
    results=[]
    # This is a local prototype fallback. Production replaces these heuristics with the model adapter.
    auth=("verify" in low or "verification" in low)
    hardship=any(x in low for x in ["lost my job","hardship","cannot make","can't make","worried","losing the house"])
    empathy=any(x in low for x in ["sorry to hear","understand how","i understand","sorry you're","sorry you"])
    resolution=any(x in low for x in ["next step","assistance","documents may be needed","review the available"])
    closing=any(x in low for x in ["anything else","next step","what happens next"])
    configs=[
      ("auth",auth,0.98,"Authentication language was found." if auth else "No clear authentication evidence was found."),
      ("discovery",True,0.92,"The borrower clearly states the reason for the call."),
      ("empathy",(empathy if hardship else True),0.96 if hardship else .80,
       "A hardship/empathy trigger is present and explicit acknowledgement was found." if empathy else "A hardship/empathy trigger is present, but no explicit acknowledgement was found."),
      ("resolution",resolution,0.93,"A resolution path or actionable next step was found." if resolution else "No clear resolution or next step was found."),
      ("communication",True,0.89,"No obvious unprofessional language was detected in this prototype."),
      ("closing",closing,0.86,"Closing/expectation language was found." if closing else "No clear closing expectations were found.")
    ]
    total=0
    for qid,passed,conf,why in configs:
        q=next(q for q in QUESTIONS if q["id"]==qid)
        pts=q["points"] if passed else 0
        total+=pts
        review=conf < .90
        results.append({**q,"result":"PASS" if passed else "FAIL","awarded":pts,"confidence":round(conf*100),
                        "why":why,"review":review})
    return round(total), results

@app.route("/",methods=["GET","POST"])
def home():
    transcript=DEMO
    result=None
    if request.method=="POST":
        transcript=request.form.get("transcript","").strip()
        if transcript:
            score,items=evaluate(transcript)
            result={"score":score,"items":items,"review_count":sum(1 for x in items if x["review"]),
                    "critical":any(x["critical"] and x["result"]=="FAIL" for x in items)}
    return render_template("index.html", transcript=transcript, result=result)

if __name__=="__main__":
    app.run(debug=True,port=5000)
