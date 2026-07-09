import { FileBarChart, LineChart, Shield, Target } from "lucide-react";
import { Section } from "./Section";
import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { TransitionEvent } from "react";
import consultingImage from "../../../Профессиональный Консалтинг.png";

const service = [
  {
    icon: Target,
    title: "Риск-профилирование",
    text: "Перед началом работы клиент должен оценить свой риск-профиль. Это нужно не для получения универсального совета, а для понимания аналитического контекста, чтобы определить, подходит ли ему выбранный формат консалтинга и какие параметры стратегии будут для него разумными.",
    listLabel: "Оцениваются:",
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
      "итоговый P/L",
      "ROI сделок",
      "наличие базового актива",
      "Win Rate по секторам",
      "размер премии",
    ],
  },
];

export function Consulting() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [orderedIndices, setOrderedIndices] = useState(() => service.map((_, index) => index));
  const [slidePhase, setSlidePhase] = useState<"idle" | "next" | "previous-setup" | "previous">(
    "idle",
  );

  const goToPrevious = () => {
    if (slidePhase !== "idle") return;

    setOrderedIndices((current) => {
      const previous = current[current.length - 1];
      return [previous, ...current.slice(0, -1)];
    });
    setActiveIndex((current) => (current - 1 + service.length) % service.length);
    setSlidePhase("previous-setup");

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        setSlidePhase("previous");
      });
    });
  };

  const goToNext = () => {
    if (slidePhase !== "idle") return;

    setActiveIndex((current) => (current + 1) % service.length);
    setSlidePhase("next");
  };

  const goToSlide = (index: number) => {
    if (slidePhase !== "idle" || index === activeIndex) return;

    setOrderedIndices(service.map((_, offset) => (index + offset) % service.length));
    setActiveIndex(index);
    setSlidePhase("idle");
  };

  const handleSliderTransitionEnd = (event: TransitionEvent<HTMLDivElement>) => {
    if (event.target !== event.currentTarget) return;

    if (slidePhase === "next") {
      setOrderedIndices((current) => [...current.slice(1), current[0]]);
    }

    setSlidePhase("idle");
  };

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
              href="https://t.me/AscentPrivate_bot"
              className="ascent-button text-primary-foreground bg-gradient-gold shadow-gold"
            >
              Получить доступ
            </a>
          </div>
        </div>

        <div className="consulting-slider">
          <div className="mb-5 flex items-center justify-between gap-4">
            <button
              type="button"
              className="consulting-slider-arrow"
              onClick={goToPrevious}
              aria-label="Предыдущая карточка"
            >
              <ChevronLeft className="size-5" />
            </button>
            <button
              type="button"
              className="consulting-slider-arrow"
              onClick={goToNext}
              aria-label="Следующая карточка"
            >
              <ChevronRight className="size-5" />
            </button>
          </div>

          <div className="consulting-slider-window" aria-live="polite">
            <div
              className="consulting-slider-track"
              data-phase={slidePhase}
              onTransitionEnd={handleSliderTransitionEnd}
            >
              {orderedIndices.map((cardIndex) => {
                const { icon: Icon, title, text, listLabel, points } = service[cardIndex];

                return (
                  <article
                    key={title}
                    className="ascent-card consulting-slider-card visual-mark bg-card/62 backdrop-blur-md p-5 sm:p-6 md:p-7 transition"
                  >
                    <div className="mb-5 flex items-center gap-4">
                      <div className="size-12 flex shrink-0 items-center justify-center border border-gold-soft text-gold">
                        <Icon className="size-5" />
                      </div>
                      <h3 className="text-[1.55rem] sm:text-2xl text-gold leading-tight">
                        {title}
                      </h3>
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
                    <span className="sr-only">Карточка {cardIndex + 1}</span>
                  </article>
                );
              })}
            </div>
          </div>

          <div className="consulting-slider-dots" aria-label="Выбор карточки">
            {service.map((item, index) => (
              <button
                key={item.title}
                type="button"
                className="consulting-slider-dot"
                data-active={activeIndex === index}
                onClick={() => goToSlide(index)}
                aria-label={`Показать карточку ${index + 1}`}
                aria-pressed={activeIndex === index}
              />
            ))}
          </div>
        </div>
      </div>
    </Section>
  );
}
