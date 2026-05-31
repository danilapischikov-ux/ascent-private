import heroImage from "../../../HERO.png";

const theses = [
  {
    title: "Фокус на рынке США",
    text: "Аналитика по инструментам американского фондового рынка и опционным стратегиям.",
  },
  {
    title: "Сценарный подход",
    text: "Каждая идея рассматривается через несколько возможных сценариев движения рынка.",
  },
  {
    title: "Контроль риска",
    text: "Риск оценивается до принятия решения, а не после наступления убытка.",
  },
  {
    title: "Private + AI",
    text: "Закрытый формат коммуникации, аналитика данных и технологичный подход к оценке рынка.",
  },
];

export function Hero() {
  return (
    <section
      id="top"
      className="section-shell scroll-mt-28 relative min-h-[100svh] flex items-end lg:items-center pt-24 sm:pt-28 pb-8 md:pb-10 px-4 sm:px-5 lg:px-10 bg-background"
    >
      <div className="absolute inset-0 z-0" aria-hidden="true">
        <div
          className="hero-media absolute inset-0 bg-cover bg-center opacity-62 md:opacity-68"
          style={{ backgroundImage: `url(${heroImage})` }}
        />
        <div className="absolute inset-0 hero-image-wash" />
        <div className="absolute inset-0 fine-grid opacity-35" />
        <div className="absolute inset-0 hero-overlay" />
        <div className="absolute inset-0 hero-vignette" />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl w-full">
        <div className="max-w-4xl reveal">
          <div className="flex items-center gap-3 mb-5 sm:mb-7">
            <div className="h-px w-12 bg-gold/60" />
            <span className="text-xs uppercase tracking-[0.26em] text-gold">
              Private Market Intelligence
            </span>
          </div>

          <h1 className="max-w-4xl text-[2.35rem] sm:text-[3.75rem] lg:text-[5.8rem] leading-[0.98] sm:leading-[0.96] text-foreground">
            Частная аналитика для <span className="text-gold italic">взвешенных решений</span> на
            рынке США
          </h1>

          <div className="mt-6 sm:mt-8 grid gap-4 max-w-3xl text-base md:text-lg text-muted-foreground leading-relaxed">
            <p>
              Ascent Private помогает клиентам оценивать рыночные возможности, опционные стратегии и
              риски через системную аналитику, сценарное моделирование и интеллектуальный подход к
              капиталу.
            </p>
            <p>
              Мы создаём закрытую аналитическую среду для клиентов, которым важно не действовать на
              эмоциях, а понимать рынок через данные, вероятность, риск-менеджмент и структуру.
            </p>
          </div>

          <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row gap-3 sm:items-center">
            <a
              href="https://t.me/InvestProfileScore_bot"
              className="ascent-button ascent-button-glow text-primary-foreground bg-gradient-gold shadow-gold"
            >
              Пройти риск-профилирование
            </a>
          </div>
        </div>

        <div className="mt-10 sm:mt-14 md:mt-20 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 border border-border/45 bg-border/35 gap-px reveal reveal-delay-2">
          {theses.map((item) => (
            <article
              key={item.title}
              className="ascent-card bg-background/56 backdrop-blur-md p-4 md:p-5"
            >
              <h3 className="text-xl text-gold mb-3">{item.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed text-justify">
                {item.text}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
