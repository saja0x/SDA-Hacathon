from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime
import anthropic
import fitz
import json
import re
import os

try:
    import rag_engine
    _rag_available = True
except ImportError as e:
    print(f"[WARNING] RAG engine not available: {e}")
    print("   Install RAG dependencies: pip install sentence-transformers chromadb openai nltk")
    print("   lookup_saudi_law will use Claude Haiku as fallback.")
    _rag_available = False
    rag_engine = None
 
from database import Base, engine
from routes import admin, auth, users
 
load_dotenv()
 
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ContractScan AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Auth Routes =====
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.on_event("startup")
def startup_event():
    """Initialize RAG system when the server starts."""
    if not _rag_available:
        print("[WARNING] RAG system skipped (dependencies not installed).")
        return
    try:
        rag_engine.init_rag()
    except Exception as e:
        print(f"[ERROR] RAG initialization failed: {e}")
        print("lookup_saudi_law will fallback to Claude Haiku.")
 
# ===== AI Client =====
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
 
# ===== Prompts =====
SYSTEM_PROMPT = """You are a Saudi freelance contract expert and legal advisor.
Analyze freelance contracts and return ONLY valid JSON — no markdown, no extra text.
 
Reference Saudi Civil Transactions Law (نظام المعاملات المدنية) and freelancer rights where relevant.
 
Risk level must match the shield score:
- high: shield_score 0–39
- medium: shield_score 40–64
- low: shield_score 65–100
 
Return this exact JSON structure:
{
  "shield_score": <number 0-100>,
  "risk_level": "<high|medium|low>",
  "client_type": "<emoji + label e.g. 🚩 Scope Creeper | 💸 Cheap Escapee | 🤝 Fair Partner>",
  "plain_summary": "<2-3 sentence plain language summary>",
  "red_flags": [{"clause": "<title>", "reason": "<why dangerous>", "fix": "<safer version>"}],
  "weak_points": [{"clause": "<title>", "suggestion": "<how to improve>"}],
  "good_clauses": ["<clause that protects the freelancer>"],
  "worst_case_story": "<2-sentence realistic worst case scenario>",
  "overall_advice": "<one clear action to take before signing>"
}"""
 
CHAT_SYSTEM_PROMPT = """You are a Saudi freelance contract expert helping a freelancer understand their contract.
 
You have access to tools — use them proactively:
- Use analyze_clause when the user asks about a specific clause
- Use lookup_saudi_law when you need to cite a specific law or legal principle
- Use summarize_party_rights when the user asks about rights
 
Format responses clearly in plain text. DO NOT use markdown like ##, **, or >. Use simple spacing and newlines for readability.
Respond in the same language the user writes in (Arabic or English)."""
 
CHAT_TOOLS = [
    {
        "name": "analyze_clause",
        "description": "Deeply analyze a specific clause from the contract.",
        "input_schema": {
            "type": "object",
            "properties": {
                "clause_title": {"type": "string", "description": "The title or name of the clause"},
                "clause_text": {"type": "string", "description": "The exact text of the clause"},
            },
            "required": ["clause_title", "clause_text"],
        },
    },
    {
        "name": "lookup_saudi_law",
        "description": "Look up what Saudi Civil Transactions Law says about a specific legal topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The legal topic to look up"},
            },
            "required": ["topic"],
        },
    },
    {
        "name": "summarize_party_rights",
        "description": "Generate a structured breakdown of rights based on the contract.",
        "input_schema": {
            "type": "object",
            "properties": {
                "party": {"type": "string", "enum": ["freelancer", "client", "both"]},
            },
            "required": ["party"],
        },
    },
]
 
 
def execute_tool(tool_name: str, tool_input: dict, contract_text: str) -> str:
    if tool_name == "analyze_clause":
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system="You are a Saudi contract law expert. Analyze the given clause concisely and precisely.",
            messages=[{
                "role": "user",
                "content": (
                    f"Clause: **{tool_input['clause_title']}**\n\n"
                    f"> {tool_input['clause_text']}\n\n"
                    "Provide:\n"
                    "1. Risk level: high / medium / low\n"
                    "2. Why it's risky for the freelancer\n"
                    "3. Which Saudi law principle it violates (if any)\n"
                    "4. A safer rewrite of this clause"
                ),
            }],
        )
        return resp.content[0].text
 
    elif tool_name == "lookup_saudi_law":
        topic = tool_input["topic"]
        # Use RAG system for real Saudi law lookup
        if _rag_available and rag_engine.is_initialized():
            try:
                hits = rag_engine.search(topic, top_k=5)
                if not hits:
                    return "لم يتم العثور على نصوص قانونية متعلقة بهذا الموضوع في نظام العمل السعودي."
                result_parts = []
                for i, hit in enumerate(hits, 1):
                    meta = hit.get("meta", {})
                    article = meta.get("article", "")
                    page = meta.get("page", "")
                    score = hit.get("score", 0)
                    header = f"المادة: {article}" if article else f"صفحة {page}"
                    result_parts.append(
                        f"{i}. {header}\n{hit['text']}\n(درجة التطابق: {score:.2f})"
                    )
                return "\n\n".join(result_parts)
            except Exception as e:
                print(f"[WARNING] RAG search failed, falling back to Claude: {e}")
        # Fallback: use Claude Haiku if RAG is not available
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system="You are a Saudi Civil Transactions Law expert. Give accurate, concise legal information relevant to freelancers.",
            messages=[{
                "role": "user",
                "content": (
                    f"What does Saudi Civil Transactions Law (نظام المعاملات المدنية, issued 2023) "
                    f"say about: **{topic}**?\n\n"
                    "Include the relevant principle, article numbers if confident, and practical implication for a Saudi freelancer."
                ),
            }],
        )
        return resp.content[0].text
 
    elif tool_name == "summarize_party_rights":
        party = tool_input.get("party", "both")
        label = {"freelancer": "the FREELANCER", "client": "the CLIENT", "both": "BOTH the freelancer and the client"}[party]
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=700,
            system="You are a Saudi freelance contract expert. Summarize rights clearly and practically.",
            messages=[{
                "role": "user",
                "content": (
                    f"Based on this contract, list all the rights of {label}.\n\n"
                    f"Contract:\n{contract_text[:4000]}\n\n"
                    "For each right: state it clearly, which clause gives it, and whether it's fair or exploitative."
                ),
            }],
        )
        return resp.content[0].text
 
    return f"Unknown tool: {tool_name}"
 
 
def run_agent_loop(system, messages, tools, contract_text, max_iterations=6):
    current_messages = [m.copy() for m in messages]
    tools_used = []
 
    for _ in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
            tools=tools,
            messages=current_messages,
        )
 
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text, tools_used
            return "", tools_used
 
        if response.stop_reason == "tool_use":
            current_messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tools_used.append(block.name)
                    result = execute_tool(block.name, block.input, contract_text)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            current_messages.append({"role": "user", "content": tool_results})
        else:
            break
 
    return "Analysis complete.", tools_used
 
 
def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()
 
 
# ===== AI Endpoints =====
@app.post("/analyze")
async def analyze_contract(
    text: str = Form(default=""),
    language: str = Form(default="ar"),
    file: UploadFile = File(default=None),
):
    contract_text = text
 
    if file and file.filename:
        contents = await file.read()
        if file.filename.endswith(".pdf"):
            contract_text = extract_text_from_pdf(contents)
        else:
            contract_text = contents.decode("utf-8", errors="ignore")
 
    if not contract_text.strip():
        return JSONResponse({"error": "No contract text provided"}, status_code=400)
 
    lang_instruction = (
        "Respond entirely in Arabic. Use simple clear Arabic a non-lawyer understands."
        if language == "ar"
        else "Respond in English. Use simple clear language."
    )
 
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT + f"\n\n{lang_instruction}",
            messages=[{"role": "user", "content": f"Analyze this contract:\n\n{contract_text[:8000]}"}],
        )
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\{[\s\S]*\}', raw)
        if match:
            raw = match.group(0)
        result = json.loads(raw)
        result["contract_text"] = contract_text[:8000]
        return JSONResponse(result)
 
    except json.JSONDecodeError:
        return JSONResponse({"error": "Failed to parse AI response"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
 
 
@app.post("/chat")
async def chat_about_contract(
    contract: str = Form(...),
    history: str = Form(default="[]"),
    question: str = Form(...),
):
    try:
        past_messages = json.loads(history)
    except Exception:
        past_messages = []
 
    messages = [
        {"role": "user", "content": f"Here is the freelance contract:\n\n{contract[:8000]}"},
        {"role": "assistant", "content": "I've read your contract. I can analyze specific clauses, look up Saudi law, and summarize your rights. What do you want to know?"},
        *past_messages,
        {"role": "user", "content": question},
    ]
 
    try:
        answer, tools_used = run_agent_loop(
            system=CHAT_SYSTEM_PROMPT,
            messages=messages,
            tools=CHAT_TOOLS,
            contract_text=contract,
        )
        return JSONResponse({"answer": answer, "tools_used": list(set(tools_used))})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
 
 
@app.get("/health")
def health():
    return {"status": "ok"}

community_posts = [
    {"id": 1, "name": "فريلانسر من الرياض", "message": "وقّعت عقداً بدون ما أقرأه وخسرت شهر عمل كامل!", "shield_score": 18, "risk_level": "high", "created_at": "2025-05-10T09:15:00"},
    {"id": 2, "name": "مصممة جرافيك", "message": "نصيحتي: لا تقبل أي عقد بدون دفعة مقدمة لا تقل عن 40%.", "shield_score": None, "risk_level": None, "created_at": "2025-05-15T14:30:00"},
]

@app.get("/community")
def get_community():
    return JSONResponse({"posts": list(reversed(community_posts))})

@app.post("/community")
async def add_post(
    name: str = Form(...),
    message: str = Form(...),
    shield_score: str = Form(default=""),
    risk_level: str = Form(default=""),
):
    score = int(shield_score) if shield_score.strip().isdigit() else None
    risk = risk_level.strip() if risk_level.strip() in ("high", "medium", "low") else None
    post = {
        "id": len(community_posts) + 1,
        "name": name.strip()[:60],
        "message": message.strip()[:500],
        "shield_score": score,
        "risk_level": risk,
        "created_at": datetime.now().isoformat(),
    }
    community_posts.append(post)
    return JSONResponse(post)
