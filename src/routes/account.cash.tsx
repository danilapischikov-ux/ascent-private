import { createFileRoute, Link } from "@tanstack/react-router";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";

export const Route = createFileRoute("/account/cash")({
  head: () => ({
    meta: [{ title: "Свободные средства — Ascent Private" }],
  }),
  component: CashPage,
});

function CashPage() {
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
            Свободные средства
          </h1>
          <p className="mt-6 text-base text-muted-foreground max-w-2xl leading-relaxed">
            Здесь будет отображаться доступный кэш, резервные средства и распределение по счетам.
          </p>
        </div>
      </section>
      <Footer />
    </main>
  );
}
