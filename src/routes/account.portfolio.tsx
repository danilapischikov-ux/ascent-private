import { createFileRoute, Link } from "@tanstack/react-router";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";

export const Route = createFileRoute("/account/portfolio")({
  head: () => ({
    meta: [{ title: "Текущий портфель — Ascent Private" }],
  }),
  component: PortfolioPage,
});

function PortfolioPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <Nav />
      <section className="pt-32 pb-24">
        <div className="mx-auto max-w-7xl px-5 lg:px-10">
          <Link
            to="/account"
            className="text-xs uppercase tracking-[0.3em] text-gold hover:opacity-80"
          >
            ← Личный кабинет
          </Link>
          <h1
            style={{ fontFamily: "var(--font-display)" }}
            className="mt-6 text-4xl md:text-5xl text-foreground"
          >
            Текущий портфель
          </h1>
          <p className="mt-6 text-base text-muted-foreground max-w-2xl leading-relaxed">
            Здесь будет отображаться состав позиций, динамика стоимости и сценарная аналитика
            портфеля.
          </p>
        </div>
      </section>
      <Footer />
    </main>
  );
}
