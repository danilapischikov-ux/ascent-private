import { createFileRoute } from "@tanstack/react-router";
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

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Ascent Private — частная аналитика для рынка США и опционов" },
      {
        name: "description",
        content:
          "Ascent Private — частная аналитическая среда для состоятельных инвесторов: рынок США, опционные стратегии, сценарный анализ и риск-интеллект.",
      },
      {
        property: "og:title",
        content: "Ascent Private — частная аналитика для рынка США",
      },
      {
        property: "og:description",
        content: "Рынок США, опционные стратегии, сценарный анализ и риск-интеллект.",
      },
    ],
  }),
  component: Index,
});

function Index() {
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
