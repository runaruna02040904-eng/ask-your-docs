import { FileText, Search, MessageCircle, Shield, Workflow } from "lucide-react";
import FadeIn from "./FadeIn";

const services = [
  {
    number: "01",
    name: "上传文档",
    desc: "支持 PDF 和 TXT 格式，拖拽或点击上传，系统自动解析并建立索引，无需任何手动配置。",
    icon: FileText,
  },
  {
    number: "02",
    name: "智能索引",
    desc: "文档经过分块、向量化处理，构建专属知识库，用户数据完全隔离，安全可靠。基于本地嵌入模型。",
    icon: Search,
  },
  {
    number: "03",
    name: "自然对话",
    desc: "用日常语言提问，AI 严格基于你的文档内容给出精准回答。支持多轮对话，让知识探索像聊天一样自然。",
    icon: MessageCircle,
  },
  {
    number: "04",
    name: "数据安全",
    desc: "用户数据完全隔离，基于向量数据库的私有知识库架构。你的文档只有你能访问。",
    icon: Shield,
  },
  {
    number: "05",
    name: "持续进化",
    desc: "基于 DeepSeek + LangChain 引擎，持续优化检索精度和回答质量。上传越多，回答越精准。",
    icon: Workflow,
  },
];

export default function ServicesSection({ onGetStarted }: { onGetStarted: () => void }) {
  return (
    <section
      className="bg-white rounded-t-[40px] sm:rounded-t-[50px] md:rounded-t-[60px]
                 px-5 sm:px-8 md:px-10 py-20 sm:py-24 md:py-32 relative z-10"
    >
      <FadeIn as="h2" y={40} delay={0} duration={0.7}>
        <h2
          className="text-[#0C0C0C] font-display font-black uppercase text-center select-none mb-16 sm:mb-20 md:mb-28"
          style={{ fontSize: "clamp(3rem, 12vw, 160px)" }}
        >
          功能
        </h2>
      </FadeIn>

      <div className="max-w-5xl mx-auto">
        {services.map((s, i) => (
          <FadeIn key={s.number} y={20} delay={i * 0.1} duration={0.7}>
            <div
              className={`flex flex-col sm:flex-row items-start gap-4 sm:gap-8 md:gap-12
                          py-8 sm:py-10 md:py-12
                          ${i < services.length - 1 ? "border-b" : ""}`}
              style={{ borderColor: "rgba(12,12,12,0.15)" }}
            >
              <span
                className="font-display font-black text-[#0C0C0C] shrink-0 leading-none select-none"
                style={{ fontSize: "clamp(3rem, 10vw, 140px)" }}
              >
                {s.number}
              </span>
              <div className="flex-1 pt-2 sm:pt-4 md:pt-6">
                <div className="flex items-center gap-3 mb-2">
                  <s.icon size={22} className="text-[#0C0C0C]/60 shrink-0" />
                  <h3
                    className="font-display font-medium uppercase text-[#0C0C0C]"
                    style={{ fontSize: "clamp(1rem, 2.2vw, 2.1rem)" }}
                  >
                    {s.name}
                  </h3>
                </div>
                <p
                  className="text-[#0C0C0C] font-light leading-relaxed max-w-2xl"
                  style={{ fontSize: "clamp(0.85rem, 1.6vw, 1.25rem)", opacity: 0.6 }}
                >
                  {s.desc}
                </p>
              </div>
            </div>
          </FadeIn>
        ))}
      </div>

      <FadeIn y={20} delay={0.6} duration={0.7} className="flex justify-center mt-16 sm:mt-20">
        <button
          onClick={onGetStarted}
          className="contact-btn rounded-full font-medium uppercase tracking-widest
                     px-10 py-3.5 text-sm md:text-base
                     hover:scale-105 transition-transform duration-300"
        >
          开始使用
        </button>
      </FadeIn>
    </section>
  );
}
