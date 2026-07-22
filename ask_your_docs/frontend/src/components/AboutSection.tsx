import { useRef, useEffect } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import FadeIn from "./FadeIn";

gsap.registerPlugin(ScrollTrigger);

const aboutText =
  "用多年的技术积累，我们专注于文档智能理解、自然语言处理和知识检索。我们真正享受为企业构建能够脱颖而出的AI产品。让你的文档流动起来，让知识触手可及。";

export default function AboutSection({ onGetStarted }: { onGetStarted: () => void }) {
  const textRef = useRef<HTMLParagraphElement>(null);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const chars = textRef.current?.querySelectorAll(".char");
      if (chars && chars.length > 0) {
        gsap.fromTo(chars,
          { opacity: 0.2 },
          { opacity: 1, stagger: 0.02, scrollTrigger: { trigger: textRef.current, start: "top 80%", end: "bottom 20%", scrub: 1 } }
        );
      }
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef}
      className="relative min-h-screen flex items-center justify-center px-5 sm:px-8 md:px-10 py-20"
      style={{ background: "#0C0C0C", overflow: "hidden" }}>
      {/* Decorative corners — picsum images with grayscale + contrast filters */}
      <FadeIn x={-80} y={0} delay={0.1} duration={0.9}
        className="absolute top-[4%] left-[1%] sm:left-[2%] md:left-[4%] z-0 pointer-events-none">
        <img src="https://picsum.photos/seed/knowledge/400" alt=""
          loading="lazy"
          className="w-[100px] sm:w-[140px] md:w-[180px] opacity-30 grayscale contrast-125 rounded-2xl" />
      </FadeIn>

      <FadeIn x={-80} y={0} delay={0.25} duration={0.9}
        className="absolute bottom-[8%] left-[3%] sm:left-[6%] md:left-[10%] z-0 pointer-events-none">
        <img src="https://picsum.photos/seed/library/400" alt=""
          loading="lazy"
          className="w-[80px] sm:w-[110px] md:w-[150px] opacity-25 grayscale contrast-125 rounded-2xl" />
      </FadeIn>

      <FadeIn x={80} y={0} delay={0.15} duration={0.9}
        className="absolute top-[4%] right-[1%] sm:right-[2%] md:right-[4%] z-0 pointer-events-none">
        <img src="https://picsum.photos/seed/intelligence/400" alt=""
          loading="lazy"
          className="w-[100px] sm:w-[140px] md:w-[180px] opacity-30 grayscale contrast-125 rounded-2xl" />
      </FadeIn>

      <FadeIn x={80} y={0} delay={0.3} duration={0.9}
        className="absolute bottom-[8%] right-[3%] sm:right-[6%] md:right-[10%] z-0 pointer-events-none">
        <img src="https://picsum.photos/seed/discovery/400" alt=""
          loading="lazy"
          className="w-[110px] sm:w-[150px] md:w-[190px] opacity-25 grayscale contrast-125 rounded-2xl" />
      </FadeIn>

      {/* Center Content */}
      <div className="relative z-10 flex flex-col items-center gap-10 sm:gap-14 md:gap-16">
        <FadeIn as="h2" y={40} delay={0} duration={0.7}>
          <h2 className="hero-heading font-display font-black uppercase leading-none tracking-tight text-center select-none"
            style={{ fontSize: "clamp(2.5rem, 10vw, 120px)", WebkitTextFillColor: "transparent" }}>
            关于我们
          </h2>
        </FadeIn>

        <div className="flex flex-col items-center gap-16 sm:gap-20 md:gap-24">
          <p ref={textRef}
            className="text-[#D7E2EA] font-medium text-center leading-relaxed max-w-[520px] px-4"
            style={{ fontSize: "clamp(0.9rem, 1.8vw, 1.2rem)" }}>
            {aboutText.split("").map((char, i) => (
              <span key={i} className="char inline" style={{ opacity: 0.2 }}>
                {char === " " ? "\u00A0" : char}
              </span>
            ))}
          </p>

          <button onClick={onGetStarted}
            className="contact-btn rounded-full font-medium uppercase tracking-widest
                       px-10 py-3.5 text-sm md:text-base whitespace-nowrap
                       hover:scale-105 transition-transform duration-300">
            开始使用
          </button>
        </div>
      </div>
    </section>
  );
}
