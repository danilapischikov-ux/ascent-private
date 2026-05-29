import { FileBarChart, LineChart, Shield, Target } from "lucide-react";
import { Section } from "./Section";
import consultingImage from "../../../Профессиональный Консалтинг.png";

const service = [
  {
    icon: Target,
    title: "Инвестиционное профилирование",
    text: "Перед началом работы мы смотрим риск-профиль клиента. Это нужно не для выдачи универсального совета, а для понимания аналитического контекста, чтобы определить, подходит ли ему выбранный формат консалтинга и какие параметры стратегии будут для него разумными.",
    listLabel: "Мы оцениваем:",
    points: [
      "цели клиента",
      "инвестиционный горизонт",
      "опыт работы с рынком",
      "отношение к риску",
      "реакцию на просадки",
      "ожидания по доходности",
    ],
  },
  {
    icon: LineChart,
    title: "Опционные стратегии на рынке США",
    text: "Ключевой инструмент нашей работы — опционные стратегии на американском фондовом рынке. Опционы позволяют работать не только с направлением движения актива, но и с волатильностью, временем, вероятностными сценариями и диапазонами цены.",
    listLabel: "Перед каждой сделкой анализируются:",
    points: [
      "ликвидность инструмента",
      "волатильность",
      "ожидаемое движение цены",
      "риск на позицию",
      "срок до экспирации",
      "поведение базового актива",
    ],
  },
  {
    icon: Shield,
    title: "Управление риском",
    text: "Контроль риска — центральная часть услуги Ascent Private. Мы не отделяем доходность от риска. Для нашего клиента важно не только заработать, но и понимать, какой риск принимается ради результата, как им управлять и как минимизировать.",
    listLabel: "Риск-менеджмент включает:",
    points: [
      "ситуационный анализ",
      "мониторинг волатильности",
      "карта рисков",
      "стресс-тестирование",
      "оценку просадки",
      "вероятностные сценарии",
    ],
  },
  {
    icon: FileBarChart,
    title: "Аналитика и отчетность",
    text: "Прозрачная отчетность создаёт доверие между клиентом и нами, а также фиксирует фактическую эффективность. Инвестор получает не только саму идею со всеми характеристиками, но и последующую отчетность по ее реализации.",
    listLabel: "Отчёты содержат:",
    points: [
      "финансовый результат",
      "обеспечение позиции",
      "объем и комиссию сделки",
      "наличие базового актива",
      "информационные выводы",
      "% роста портфеля",
    ],
  },
];

export function Consulting() {
  return (
    <Section
      id="consulting"
      image={consultingImage}
      imagePosition="center right"
      eyebrow="Профессиональный консалтинг"
      title={
        <>
          Один сервис. <span className="text-gold italic">Глубокая аналитика.</span>
        </>
      }
      subtitle="Мы предоставляем продвинутые консультационные услуги, сценарное моделирование и торговые стратегии, специализируясь на рынках акций и опционов США, оценкой контроля риска, аналитическим сопровождением и регулярной отчетностью."
    >
      <div className="reveal reveal-delay-1">
        <div className="mx-auto mb-8 sm:mb-10 md:mb-12 max-w-4xl text-center">
          <p
            className="text-xl md:text-2xl text-foreground leading-relaxed"
            style={{ fontFamily: "var(--font-display)", fontWeight: 500, letterSpacing: 0 }}
          >
            Ascent Private предлагает одну ключевую услугу — аналитический сервис для инвесторов,
            которые хотят принимать решения на основе данных, структуры и заранее понятных рисков,
            контролируя устойчивый рост своего капитала
          </p>
          <p className="mt-5 text-sm md:text-base text-muted-foreground leading-relaxed">
            Мы помогаем инвестору увидеть рынок глубже: понять, какие возможности существуют, какие
            сценарии возможны, где находятся основные риски и какие параметры нужно учитывать перед
            принятием решения.
          </p>
          <p className="mt-4 text-sm md:text-base text-muted-foreground leading-relaxed">
            Наша задача — не просто искать доходность, а выстраивать управляемый процесс, где каждое
            решение имеет логику, ограничения и сценарий действий.
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 md:gap-6 lg:gap-8">
          {service.map(({ icon: Icon, title, text, listLabel, points }) => (
            <article
              key={title}
              className="ascent-card bg-card/82 backdrop-blur-md p-5 sm:p-6 md:p-7 transition"
            >
              <div className="mb-5 flex items-center gap-4">
                <div className="size-12 flex shrink-0 items-center justify-center border border-gold-soft text-gold">
                  <Icon className="size-5" />
                </div>
                <h3 className="text-[1.55rem] sm:text-2xl text-gold leading-tight">{title}</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed text-left sm:text-justify">
                {text}
              </p>
              <h3 className="mt-6 mb-3 text-xl text-gold">{listLabel}</h3>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-x-5 gap-y-2.5">
                {points.map((point) => (
                  <li
                    key={point}
                    className="flex items-start gap-3 text-sm text-muted-foreground leading-relaxed"
                  >
                    <span className="mt-2 size-1.5 bg-gold rounded-full shrink-0" />
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </div>
    </Section>
  );
}
