import { useState, useRef, type FormEvent } from "react";
import {
  Send, Bot, User, Upload, FileText,
  LogOut, Menu, MessageSquare,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { uploadDocument, askQuestion } from "../api/client";
import type { Message } from "../api/client";

/* ===== Chat Panel ===== */
function ChatPanel({ token, messages, onSend }: {
  token: string; messages: Message[]; onSend: (msg: Message) => void;
}) {
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const prevLen = useRef(0);

  if (messages.length !== prevLen.current) {
    prevLen.current = messages.length;
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || sending) return;
    setInput("");
    onSend({ role: "user", content: q });
    setSending(true);
    try {
      const res = await askQuestion(token, q);
      onSend({ role: "assistant", content: res.answer });
    } catch (err: unknown) {
      onSend({ role: "assistant", content: "抱歉，出错了：" + (err instanceof Error ? err.message : "未知错误") });
    } finally { setSending(false); }
  };

  return (
    <div className="flex flex-col h-full" style={{ background: "#0C0C0C" }}>
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center px-6">
          <Bot size={40} className="mb-4" style={{ color: "rgba(215,226,234,0.2)" }} />
          <p className="text-sm" style={{ color: "rgba(215,226,234,0.6)" }}>上传文档后，在这里提问</p>
          <p className="text-xs mt-1" style={{ color: "rgba(215,226,234,0.3)" }}>例如：这篇文章的主要内容是什么？</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 items-start ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
              <div className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5"
                style={{ background: msg.role === "user" ? "rgba(215,226,234,0.1)" : "rgba(215,226,234,0.05)" }}>
                {msg.role === "user" ? <User size={13} style={{ color: "rgba(215,226,234,0.6)" }} />
                  : <Bot size={13} style={{ color: "rgba(215,226,234,0.6)" }} />}
              </div>
              <div className="max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
                style={{ background: msg.role === "user" ? "rgba(182,0,168,0.15)" : "rgba(215,226,234,0.05)", color: "#D7E2EA" }}>
                {msg.content}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex gap-3 items-start">
              <div className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5" style={{ background: "rgba(215,226,234,0.05)" }}>
                <Bot size={13} style={{ color: "rgba(215,226,234,0.6)" }} />
              </div>
              <div className="max-w-[75%] rounded-2xl px-4 py-2.5" style={{ background: "rgba(215,226,234,0.05)" }}>
                <span className="text-sm animate-pulse" style={{ color: "rgba(215,226,234,0.5)" }}>思考中</span>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>
      )}
      <div className="p-4" style={{ borderTop: "1px solid rgba(215,226,234,0.06)" }}>
        <form onSubmit={handleSubmit} className="flex gap-2.5">
          <input value={input} onChange={(e) => setInput(e.target.value)} type="text"
            placeholder="输入你的问题..."
            className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none transition-colors"
            style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(215,226,234,0.08)", color: "#D7E2EA" }} />
          <button type="submit" disabled={!input.trim() || sending}
            className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 disabled:opacity-30"
            style={{ background: "rgba(215,226,234,0.08)" }}>
            <Send size={15} style={{ color: "#D7E2EA" }} />
          </button>
        </form>
      </div>
    </div>
  );
}

/* ===== Upload Panel ===== */
function UploadPanel({ token }: { token: string }) {
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setStatus("上传中...");
    try {
      const res = await uploadDocument(token, file);
      setStatus(res.message);
      setTimeout(() => setStatus(""), 3000);
    } catch (err: unknown) {
      setStatus("上传失败：" + (err instanceof Error ? err.message : "未知错误"));
    } finally { setUploading(false); if (fileRef.current) fileRef.current.value = ""; }
  };

  return (
    <div className="flex-1 p-4">
      <div className="rounded-2xl p-6 text-center" style={{ background: "rgba(215,226,234,0.04)", border: "1px solid rgba(215,226,234,0.08)" }}>
        <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3" style={{ background: "rgba(215,226,234,0.06)" }}>
          <Upload size={20} style={{ color: "rgba(215,226,234,0.6)" }} />
        </div>
        <p className="text-lg mb-1 font-display font-medium" style={{ color: "#D7E2EA" }}>上传文档</p>
        <p className="text-xs mb-5" style={{ color: "rgba(215,226,234,0.4)" }}>支持 PDF / TXT 格式</p>
        <input ref={fileRef} type="file" accept=".pdf,.txt" onChange={handleFile} className="hidden" id="sd-upload2" />
        <label htmlFor="sd-upload2"
          className="inline-block rounded-full px-5 py-2 text-xs cursor-pointer hover:opacity-80 transition-opacity"
          style={{ background: "rgba(215,226,234,0.08)", color: "#D7E2EA", border: "1px solid rgba(215,226,234,0.15)" }}>
          {uploading ? "上传中..." : "选择文件"}
        </label>
        {status && <p className="text-xs mt-3" style={{ color: "rgba(215,226,234,0.5)" }}>{status}</p>}
      </div>
      <div className="mt-4 space-y-1.5">
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-xl" style={{ background: "rgba(215,226,234,0.03)" }}>
          <FileText size={14} style={{ color: "rgba(215,226,234,0.4)" }} />
          <span className="text-xs" style={{ color: "rgba(215,226,234,0.4)" }}>.pdf</span>
        </div>
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-xl" style={{ background: "rgba(215,226,234,0.03)" }}>
          <FileText size={14} style={{ color: "rgba(215,226,234,0.4)" }} />
          <span className="text-xs" style={{ color: "rgba(215,226,234,0.4)" }}>.txt</span>
        </div>
      </div>
    </div>
  );
}

/* ===== Dashboard Layout ===== */
interface DashboardLayoutProps {
  token: string; username: string; onLogout: () => void;
}

export default function DashboardLayout({ token, username, onLogout }: DashboardLayoutProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [tab, setTab] = useState<"chat" | "upload">("chat");
  const handleSend = (msg: Message) => setMessages(prev => [...prev, msg]);

  return (
    <div className="h-screen flex flex-col" style={{ background: "#0C0C0C" }}>
      <header className="flex items-center justify-between px-6 py-3" style={{ borderBottom: "1px solid rgba(215,226,234,0.06)" }}>
        <div className="flex items-center gap-3">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/5 transition-colors">
            <Menu size={15} style={{ color: "rgba(215,226,234,0.6)" }} />
          </button>
          <span className="text-xl tracking-tight font-display font-bold" style={{ color: "#D7E2EA" }}>AskYourDocs</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-xl px-3 py-1.5" style={{ background: "rgba(215,226,234,0.05)" }}>
            <div className="w-6 h-6 rounded-full flex items-center justify-center" style={{ background: "rgba(215,226,234,0.1)" }}>
              <span className="text-xs font-medium" style={{ color: "rgba(215,226,234,0.6)" }}>{username.charAt(0).toUpperCase()}</span>
            </div>
            <span className="text-sm" style={{ color: "rgba(215,226,234,0.6)" }}>{username}</span>
          </div>
          <button onClick={onLogout} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/5 transition-colors">
            <LogOut size={14} style={{ color: "rgba(215,226,234,0.5)" }} />
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <AnimatePresence>
          {sidebarOpen && (
            <motion.aside
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 256, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
              className="flex flex-col shrink-0 overflow-hidden"
              style={{ borderRight: "1px solid rgba(215,226,234,0.06)" }}>
              <div className="flex gap-2 p-4 pb-0">
                {(["chat", "upload"] as const).map(t => (
                  <button key={t} onClick={() => setTab(t)}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs font-medium transition-all"
                    style={{ background: tab === t ? "rgba(215,226,234,0.1)" : "rgba(215,226,234,0.04)", color: tab === t ? "#D7E2EA" : "rgba(215,226,234,0.5)" }}>
                    {t === "chat" ? <MessageSquare size={13} /> : <Upload size={13} />}
                    {t === "chat" ? "对话" : "上传"}
                  </button>
                ))}
              </div>
              {tab === "upload" ? <UploadPanel token={token} /> : (
                <div className="flex-1 flex flex-col items-center justify-center text-center px-4">
                  <MessageSquare size={24} style={{ color: "rgba(215,226,234,0.12)" }} />
                  <p className="text-xs mt-2" style={{ color: "rgba(215,226,234,0.3)" }}>上传文档后开始对话</p>
                </div>
              )}
            </motion.aside>
          )}
        </AnimatePresence>
        <main className="flex-1 flex flex-col min-w-0">
          <ChatPanel token={token} messages={messages} onSend={handleSend} />
        </main>
      </div>
    </div>
  );
}
