import FadeIn from "./FadeIn";

interface NavProps {
  onGetStarted: () => void;
}

const links = [
  { label: "首页", key: "home" },
  { label: "功能", key: "features" },
  { label: "项目", key: "projects" },
  { label: "联系", key: "contact" },
];

export default function Nav({ onGetStarted }: NavProps) {
  const scrollTo = (key: string) => {
    if (key === "home") window.scrollTo({ top: 0, behavior: "smooth" });
    else if (key === "features") {
      const el = document.getElementById("features-section");
      if (el) el.scrollIntoView({ behavior: "smooth" });
    } else if (key === "projects") {
      const el = document.getElementById("projects-section");
      if (el) el.scrollIntoView({ behavior: "smooth" });
    } else if (key === "contact") onGetStarted();
  };

  return (
    <FadeIn as="nav" y={-20} delay={0} duration={0.7}>
      <div className="flex items-center justify-between px-6 md:px-10 pt-6 md:pt-8">
        <span
          className="text-lg md:text-xl font-display font-bold tracking-wide"
          style={{ fontFamily: "Kanit, sans-serif", color: "#D7E2EA" }}
        >
          AskYourDocs
        </span>
        <div className="flex items-center gap-6 md:gap-10">
          {links.map((l) => (
            <button
              key={l.key}
              onClick={() => scrollTo(l.key)}
              className="text-sm md:text-lg lg:text-[1.4rem] uppercase tracking-wider font-medium transition-opacity duration-200 hover:opacity-70"
              style={{
                color: l.key === "home" ? "#D7E2EA" : "rgba(215,226,234,0.8)",
              }}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>
    </FadeIn>
  );
}
