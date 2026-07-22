import { useRef, type ReactNode } from "react";
import { motion, useMotionValue } from "framer-motion";
import { FileSearch } from "lucide-react";
import FadeIn from "./FadeIn";

/* ===== Magnet ===== */
function Magnet({
  children, padding = 150, strength = 3, className = "",
}: {
  children: ReactNode; padding?: number; strength?: number; className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = ref.current?.getBoundingClientRect();
    if (!rect) return;
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = e.clientX - cx;
    const dy = e.clientY - cy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > padding) { x.set(0); y.set(0); return; }
    x.set(dx / strength);
    y.set(dy / strength);
  };

  const handleMouseLeave = () => { x.set(0); y.set(0); };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ x, y, willChange: "transform" }}
      transition={{ type: "spring", stiffness: 150, damping: 15, mass: 0.1 }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ===== HeroSection ===== */
interface HeroSectionProps { onGetStarted: () => void; }

export default function HeroSection({ onGetStarted }: HeroSectionProps) {
  return (
    <section className="relative h-screen flex flex-col" style={{ overflowX: "clip", background: "#0C0C0C" }}>
      {/* Gradient Heading — reduced size to fit "AskYourDocs" without overflow */}
      <div className="flex-1 flex items-center justify-center overflow-hidden px-4">
        <FadeIn as="h1" y={40} delay={0.15} duration={0.8} className="w-full text-center">
          <h1
            className="hero-heading font-display font-black uppercase tracking-tight leading-[0.9] inline-block w-full text-center select-none"
            style={{
              fontSize: "clamp(2rem, 7.5vw, 7.5vw)",
              WebkitTextFillColor: "transparent",
            }}
          >
            AskYour<br className="sm:hidden" />
            <span className="hidden sm:inline"> </span>Docs
          </h1>
        </FadeIn>
      </div>

      {/* Center Magnet Icon */}
      <Magnet padding={150} strength={3}
        className="absolute left-1/2 -translate-x-1/2 z-10
                   top-[55%] -translate-y-1/2
                   sm:top-auto sm:translate-y-0 sm:bottom-[6%] md:bottom-[8%]
                   w-[140px] sm:w-[200px] md:w-[280px] lg:w-[340px]"
      >
        <FadeIn y={30} delay={0.6} duration={0.8}>
          <div className="w-full aspect-square rounded-[32px] sm:rounded-[40px] flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 100%)" }}>
            <FileSearch size={60} strokeWidth={1} style={{ color: "rgba(187,204,215,0.5)" }} />
          </div>
        </FadeIn>
      </Magnet>

      {/* Bottom Bar */}
      <div className="flex items-end justify-between pb-6 sm:pb-7 md:pb-8 px-6 md:px-10 z-20">
        <FadeIn as="p" y={20} delay={0.35} duration={0.7} className="max-w-[140px] sm:max-w-[200px] md:max-w-[240px]">
          <p className="text-[#D7E2EA] font-light uppercase tracking-wide leading-snug"
            style={{ fontSize: "clamp(0.65rem, 1.2vw, 1.3rem)" }}>
            上传文档，用自然语言提问，AI 立刻给出精准答案
          </p>
        </FadeIn>

        <FadeIn y={20} delay={0.5} duration={0.7}>
          <button onClick={onGetStarted}
            className="contact-btn rounded-full font-medium uppercase tracking-widest
                       px-6 py-2.5 sm:px-8 sm:py-3 md:px-10 md:py-3.5
                       text-[10px] sm:text-xs md:text-sm whitespace-nowrap
                       hover:scale-105 transition-transform duration-300">
            开始使用
          </button>
        </FadeIn>
      </div>
    </section>
  );
}
