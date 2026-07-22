import { X } from "lucide-react";
import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { login, register } from "../api/client";

interface AuthDialogProps {
  isOpen: boolean;
  mode: "login" | "register";
  onClose: () => void;
  onSuccess: (token: string, username: string) => void;
  onSwitchMode: () => void;
}

export default function AuthDialog({
  isOpen,
  mode,
  onClose,
  onSuccess,
  onSwitchMode,
}: AuthDialogProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await register(username, password);
        setUsername("");
        setPassword("");
        onSwitchMode();
      } else {
        const res = await login(username, password);
        onSuccess(res.access_token, username);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "操作失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-sm rounded-2xl p-8"
        style={{ background: "#0C0C0C", border: "1px solid rgba(215,226,234,0.12)" }}
      >
        <button onClick={onClose} className="absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center hover:bg-white/5 transition-colors" style={{ color: "#D7E2EA" }}>
          <X size={15} />
        </button>

        <h2 className="text-3xl tracking-tight mb-1 font-display font-bold" style={{ color: "#D7E2EA" }}>
          {mode === "login" ? "欢迎回来" : "加入我们"}
        </h2>
        <p className="text-sm mb-7" style={{ color: "rgba(215,226,234,0.6)" }}>
          {mode === "login" ? "登录后继续你的探索之旅" : "创建账号，开始智能文档问答"}
        </p>

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <input
            type="text" placeholder="用户名" value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-3 rounded-xl text-sm outline-none transition-colors"
            style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(215,226,234,0.1)", color: "#D7E2EA" }}
            required minLength={2}
          />
          <input
            type="password" placeholder="密码" value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 rounded-xl text-sm outline-none transition-colors"
            style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(215,226,234,0.1)", color: "#D7E2EA" }}
            required minLength={4}
          />
          {error && <p className="text-red-400 text-xs">{error}</p>}
          <button type="submit" disabled={loading}
            className="contact-btn w-full rounded-full py-3 text-sm font-medium uppercase tracking-widest"
          >
            {loading ? "处理中..." : mode === "login" ? "登录" : "创建账号"}
          </button>
        </form>

        <p className="text-center text-xs mt-6" style={{ color: "rgba(215,226,234,0.5)" }}>
          {mode === "login" ? "还没有账号？" : "已有账号？"}
          <button onClick={onSwitchMode} className="ml-1 transition-colors" style={{ color: "#D7E2EA" }}>
            {mode === "login" ? "注册" : "登录"}
          </button>
        </p>
      </motion.div>
    </div>
  );
}
