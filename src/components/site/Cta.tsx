export function Cta() {
  return (
    <section
      id="cta"
      className="section-shell scroll-mt-24 md:scroll-mt-28 relative bg-background py-5 md:py-7 lg:py-8 px-4 sm:px-5 lg:px-10"
    >
      <div className="relative z-10 mx-auto max-w-7xl">
        <div className="mx-auto max-w-4xl text-center reveal">
          <p
            className="text-xl md:text-2xl text-foreground leading-relaxed"
            style={{ fontFamily: "var(--font-display)", fontWeight: 500, letterSpacing: 0 }}
          >
            Ascent Private создан для тех, кто хочет управлять капиталом осознанно: с понятной
            стратегией, контролем риска, профессиональной аналитикой и прозрачной отчетностью.
          </p>
          <p className="mx-auto mt-5 max-w-3xl text-sm md:text-base text-muted-foreground leading-relaxed">
            Если вы рассматриваете профессиональный аналитический слой для своих решений на рынке
            США – начните с ознакомительного доступа.
          </p>
          <div className="mt-8 flex justify-center">
            <a
              href="https://t.me/+qAf6qjG9MbFiMGVi"
              className="ascent-button text-primary-foreground bg-gradient-gold shadow-gold"
            >
              Получить доступ
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
