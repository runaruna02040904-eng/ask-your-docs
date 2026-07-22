from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import engine, Base          # 改为绝对导入
from app.models import User, Document          # 改为绝对导入
from app.schemas import UserCreate, UserOut, Token  # 改为绝对导入
from app.auth import (                          # 改为绝对导入
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_db
)
from app.rag_engine import add_document_to_vectorstore
from core.agent import default_agent
from fastapi.responses import StreamingResponse  # 改为绝对导入
import pypdf
import io



Base.metadata.create_all(bind=engine)

app = FastAPI(title="AskYourDocs")

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    hashed_pwd = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = ""
    if file.filename.endswith(".pdf"):
        pdf_reader = pypdf.PdfReader(io.BytesIO(await file.read()))
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                content += text + "\n"
    else:
        content = (await file.read()).decode("utf-8", errors="ignore")

    if not content.strip():
        raise HTTPException(status_code=400, detail="无法提取文本内容")

    doc = Document(filename=file.filename, content=content, owner_id=current_user.id)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    chunk_count = add_document_to_vectorstore(content, current_user.id, file.filename)
    return {"message": f"上传成功，已处理 {chunk_count} 个文本块", "doc_id": doc.id}

@app.post("/chat")
async def chat(
    question: str,
    current_user: User = Depends(get_current_user),
):
    state = {
        "question": question,
        "user_id": current_user.id,
        "context": "",
        "answer": "",
        "history": [],
        "iteration": 0,
    }

    async def event_generator():
        async for event in default_agent._graph.astream_events(
            state, version="v1"
        ):
            kind = event["event"]

            # Token-level streaming from the chat model
            if kind == "on_chat_model_stream":
                chunk = event["data"].get("chunk")
                if chunk is not None and chunk.content:
                    yield f"data: {chunk.content}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )