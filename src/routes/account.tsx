import { createFileRoute, Link } from "@tanstack/react-router";
import { Nav } from "@/components/site/Nav";
import { Footer } from "@/components/site/Footer";
import { Wallet, Briefcase } from "lucide-react";

export const Route = createFileRoute("/account")({
  head: () => ({
    meta: [
      { title: "Личный кабинет — Ascent Private" },
      {
        name: "description",
        content: "Личный кабинет инвестора Ascent Private: текущий портфель и свободные средства.",
      },
    ],
  }),
  component: AccountPage,
});

const blocks = [
  {
    to: "/account/portfolio",
    label: "Текущий портфель",
    description: "Состав позиций, динамика и аналитика портфеля.",
    Icon: Briefcase,
  },
  {
    to: "/account/cash",
    label: "Свободные средства",
    description: "Доступный кэш, резервы и распределение по счетам.",
    Icon: Wallet,
  },
] as const;

function AccountPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <Nav />
      <section className="pt-32 pb-24">
        <div className="mx-auto max-w-7xl px-5 lg:px-10">
          <p className="text-xs uppercase tracking-[0.3em] text-gold mb-5">Личный кабинет</p>
          <h1
            style={{ fontFamily: "var(--font-display)" }}
            className="text-4xl md:text-5xl lg:text-6xl text-foreground leading-tight max-w-3xl"
          >
            Ваша частная инвестиционная среда
          </h1>

          <div className="mt-14 grid grid-cols-1 md:grid-cols-2 gap-6">
            {blocks.map(({ to, label, description, Icon }) => (
              <Link
                key={to}
                to={to}
                className="group relative overflow-hidden rounded-sm border border-border bg-card/40 backdrop-blur-sm p-8 md:p-10 hover:border-gold transition-colors"
              >
                <div className="flex items-start justify-between gap-6">
                  <div>
                    <h2
                      style={{ fontFamily: "var(--font-display)" }}
                      className="text-2xl md:text-3xl text-foreground mb-3"
                    >
                      {label}
                    </h2>
                    <p className="text-sm text-muted-foreground leading-relaxed max-w-sm">
                      {description}
                    </p>
                  </div>
                  <Icon className="h-8 w-8 text-gold shrink-0 transition-transform group-hover:translate-x-1" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
