import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Nav } from "@/components/site/Nav";
import { Hero } from "@/components/site/Hero";
import { Solve } from "@/components/site/Solve";
import { Consulting } from "@/components/site/Consulting";
import { Process } from "@/components/site/Process";
import { Audience } from "@/components/site/Audience";
import { Why } from "@/components/site/Why";
import { Faq } from "@/components/site/Faq";
import { Cta } from "@/components/site/Cta";
import { Footer } from "@/components/site/Footer";
import { Toaster } from "@/components/ui/sonner";
import "./styles.css";

(window as Window & { __ASCENT_STATIC_BUILD__?: string }).__ASCENT_STATIC_BUILD__ = "2026-05-30-01";

function StaticApp() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <Nav />
      <Hero />
      <Solve />
      <Consulting />
      <Process />
      <Audience />
      <Why />
      <Faq />
      <Cta />
      <Footer />
      <Toaster />
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <StaticApp />
  </StrictMode>,
);
