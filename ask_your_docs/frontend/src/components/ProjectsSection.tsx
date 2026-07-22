import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { ArrowUpRight } from "lucide-react";

const projects = [
  {
    number: "01", label: "场景", name: "文档问答", sub: "企业知识库",
    images: [
      { col: 1, src: "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&q=80&fit=crop", h: "clamp(130px,16vw,230px)" },
      { col: 1, src: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&q=80&fit=crop", h: "clamp(160px,22vw,340px)" },
      { col: 2, src: "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&q=80&fit=crop" },
    ],
  },
  {
    number: "02", label: "场景", name: "智能研究", sub: "学术分析",
    images: [
      { col: 1, src: "https://images.unsplash.com/photo-1509228627152-72ae9ae6848d?w=600&q=80&fit=crop", h: "clamp(130px,16vw,230px)" },
      { col: 1, src: "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=600&q=80&fit=crop", h: "clamp(160px,22vw,340px)" },
      { col: 2, src: "https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=600&q=80&fit=crop" },
    ],
  },
  {
    number: "03", label: "场景", name: "合同审查", sub: "法律合规",
    images: [
      { col: 1, src: "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=600&q=80&fit=crop", h: "clamp(130px,16vw,230px)" },
      { col: 1, src: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=600&q=80&fit=crop", h: "clamp(160px,22vw,340px)" },
      { col: 2, src: "https://images.unsplash.com/photo-1505663912509-362e4bf47693?w=600&q=80&fit=crop" },
    ],
  },
];

function Card({ p, index, total, onGetStarted }: {
  p: typeof projects[0]; index: number; total: number; onGetStarted: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "start start"],
  });
  const targetScale = 1 - (total - 1 - index) * 0.03;
  const scale = useTransform(scrollYProgress, [0, 1], [0.85, targetScale]);

  return (
    <div ref={ref} className="sticky" style={{ top: `${24 + index * 28}px`, height: "85vh" }}>
      <motion.div
        style={{ scale, originY: "top", background: "#0C0C0C", borderColor: "#D7E2EA" }}
        className="rounded-[40px] sm:rounded-[50px] md:rounded-[60px] border-2 p-4 sm:p-6 md:p-8 h-full flex flex-col"
      >
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <div className="flex items-center gap-4 sm:gap-6">
            <span className="font-display font-black text-[#D7E2EA] leading-none select-none"
              style={{ fontSize: "clamp(3rem,10vw,140px)" }}>{p.number}</span>
            <div>
              <p className="font-display font-medium uppercase text-[#D7E2EA]/60 text-xs sm:text-sm">{p.label}</p>
              <p className="font-display font-bold uppercase text-[#D7E2EA] leading-tight"
                style={{ fontSize: "clamp(1rem,2.2vw,2.1rem)" }}>{p.name}</p>
              <p className="font-display text-[#D7E2EA]/50 text-xs sm:text-sm">{p.sub}</p>
            </div>
          </div>
          <button onClick={onGetStarted}
            className="rounded-full border-2 border-[#D7E2EA] px-8 py-3 sm:px-10 sm:py-3.5 font-medium uppercase tracking-widest text-xs sm:text-sm text-[#D7E2EA] hover:bg-[#D7E2EA]/10 transition-colors shrink-0 ml-4">
            开始<ArrowUpRight size={14} className="inline ml-1" />
          </button>
        </div>

        <div className="flex-1 flex gap-3 sm:gap-4 min-h-0">
          <div className="flex flex-col gap-3 sm:gap-4" style={{ flex: 0.4 }}>
            <div className="rounded-[40px] sm:rounded-[50px] md:rounded-[60px] overflow-hidden" style={{ height: p.images[0].h }}>
              <img src={p.images[0].src} alt="" className="w-full h-full object-cover" />
            </div>
            <div className="rounded-[40px] sm:rounded-[50px] md:rounded-[60px] overflow-hidden flex-1">
              <img src={p.images[1].src} alt="" className="w-full h-full object-cover" />
            </div>
          </div>
          <div className="flex-1 rounded-[40px] sm:rounded-[50px] md:rounded-[60px] overflow-hidden" style={{ flex: 0.6 }}>
            <img src={p.images[2].src} alt="" className="w-full h-full object-cover" />
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function ProjectsSection({ onGetStarted }: { onGetStarted: () => void }) {
  return (
    <section id="projects-section"
      className="-mt-10 sm:-mt-12 md:-mt-14 z-10 relative
                 rounded-t-[40px] sm:rounded-t-[50px] md:rounded-t-[60px]
                 px-5 sm:px-8 md:px-10 py-20 sm:py-24 md:py-32"
      style={{ background: "#0C0C0C" }}>
      <h2 className="hero-heading font-display font-black uppercase text-center leading-none tracking-tight select-none mb-16 sm:mb-20 md:mb-28"
        style={{ fontSize: "clamp(3rem,12vw,160px)", WebkitTextFillColor: "transparent" }}>
        应用场景
      </h2>
      <div className="max-w-6xl mx-auto">
        {projects.map((p, i) => (
          <Card key={p.number} p={p} index={i} total={projects.length} onGetStarted={onGetStarted} />
        ))}
      </div>
    </section>
  );
}
