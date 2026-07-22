import { useState } from "react";
import { createPortal } from "react-dom";
import Nav from "./components/Nav";
import HeroSection from "./components/HeroSection";
import MarqueeSection from "./components/MarqueeSection";
import AboutSection from "./components/AboutSection";
import ServicesSection from "./components/ServicesSection";
import ProjectsSection from "./components/ProjectsSection";
import AuthDialog from "./components/AuthDialog";
import DashboardLayout from "./components/DashboardLayout";

type PageState =
  | { view: "landing" }
  | { view: "dashboard"; token: string; username: string };

export default function App() {
  const [page, setPage] = useState<PageState>({ view: "landing" });
  const [authOpen, setAuthOpen] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");

  const handleLoginSuccess = (token: string, username: string) => {
    setPage({ view: "dashboard", token, username });
    setAuthOpen(false);
  };

  const handleLogout = () => setPage({ view: "landing" });
  const openAuth = (mode: "login" | "register") => { setAuthMode(mode); setAuthOpen(true); };

  if (page.view === "dashboard") {
    return <DashboardLayout token={page.token} username={page.username} onLogout={handleLogout} />;
  }

  return (
    <main style={{ overflowX: "clip", background: "#0C0C0C" }}>
      <Nav onGetStarted={() => openAuth("register")} />
      <HeroSection onGetStarted={() => openAuth("register")} />
      <MarqueeSection />
      <AboutSection onGetStarted={() => openAuth("register")} />
      <ServicesSection onGetStarted={() => openAuth("register")} />
      <ProjectsSection onGetStarted={() => openAuth("register")} />
      {createPortal(
        <AuthDialog
          isOpen={authOpen} mode={authMode}
          onClose={() => setAuthOpen(false)}
          onSuccess={handleLoginSuccess}
          onSwitchMode={() => setAuthMode(authMode === "login" ? "register" : "login")}
        />,
        document.body
      )}
    </main>
  );
}
