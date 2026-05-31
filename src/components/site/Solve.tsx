import { BrainCircuit, Eye, Layers3, SearchCheck, ShieldAlert, Waves } from "lucide-react";
import { Section } from "./Section";
import solveImage from "../../../Что мы решаем.png";

const cards = [
  {
    icon: Layers3,
    title: "Хаотичные инвестиционные идеи",
    text: "Инвестор часто сталкивается с большим количеством мнений: аналитики, банки, брокеры, Telegram-каналы, новости, знакомые, рыночные прогнозы. Но большое количество информации не означает качество решений.",
    action:
      "Структурируем идеи через аналитику: оцениваем рыночный контекст, волатильность, ликвидность, вероятные сценарии и риск-профиль инструмента.",
  },
  {
    icon: ShieldAlert,
    title: "Непонимание реального риска",
    text: "На первый взгляд идея может выглядеть привлекательной, но скрывать высокий риск: резкую волатильность, слабую ликвидность, неблагоприятное соотношение риска и потенциальной доходности.",
    action:
      "Показываем риск заранее: возможную просадку, негативные сценарии, чувствительность к движению цены, влияние времени и волатильности.",
  },
  {
    icon: Waves,
    title: "Эмоциональные решения",
    text: "Когда рынок растёт, инвестору сложно не увеличивать риск. Когда рынок падает — сложно не закрывать позиции в панике. Эмоции часто вредят сильнее, чем сам рынок.",
    action:
      "Формируем аналитическую рамку: что смотреть, какие уровни риска учитывать, где заканчивается рациональное решение и начинается эмоциональная реакция.",
  },
  {
    icon: BrainCircuit,
    title: "Сложность опционных стратегий",
    text: "Опционы дают гибкость, но требуют понимания волатильности, времени до экспирации, вероятности движения, структуры позиции и поведения базового актива.",
    action:
      "Убираем сложную теорию и внутреннюю механику процесса работы опционов. Даем четко сформулированную идею, которая не требует расшифровки и может сразу быть применена клиентом.",
  },
  {
    icon: SearchCheck,
    title: "Недостаток прозрачной аналитики",
    text: "Многие инвестиционные предложения звучат красиво, но скрывают «подводные камни»: почему идея появилась, какие данные её подтверждают и что может пойти не так.",
    action:
      "Нейтрализуем скрытые риски. Даём идеи, которые прошли многослойную экспертную проверку, учитываем логику идеи, факторы риска, сценарии, ключевые метрики и ограничения.",
  },
  {
    icon: Eye,
    title: "Отсутствие второго эксперта",
    text: "Даже опытному инвестору полезно получить независимую аналитическую оценку перед принятием решения, особенно если речь идёт о крупном капитале или сложных инструментах.",
    action:
      "Выступаем как аналитический слой: помогаем проверить идею, увидеть слабые места, оценить риск и подготовить более взвешенное решение.",
  },
];

export function Solve() {
  return (
    <Section
      id="solve"
      image={solveImage}
      eyebrow="Что мы решаем"
      title={
        <>
          Помогаем видеть рынок <span className="text-gold italic">системно</span>, а не хаотично
        </>
      }
      subtitle="На рынке много возможностей, но без системы они превращаются в источник стресса. Ascent Private помогает отделять рыночный шум от структурированной аналитики и заранее понимать возможные риски."
    >
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 md:gap-8 reveal reveal-delay-1">
        {cards.map((card) => {
          const Icon = card.icon;

          return (
            <article
              key={card.title}
              className="ascent-card solve-card visual-mark bg-card/62 backdrop-blur-md p-5 md:p-7 xl:p-8 min-w-0 transition flex flex-col"
            >
              <div className="solve-card-main">
                <div className="relative mb-4 flex min-h-12 items-start justify-center px-12 text-center">
                  <h3 className="text-[1.55rem] sm:text-2xl text-gold mb-1 leading-tight xl:min-h-16">
                    {card.title}
                  </h3>
                  <div className="absolute right-0 top-0 size-11 flex shrink-0 items-center justify-center border border-gold-soft text-gold/90">
                    <Icon className="size-5" />
                  </div>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed text-left sm:text-justify">
                  {card.text}
                </p>
              </div>

              <button type="button" className="solve-action-trigger">
                Что мы делаем
              </button>

              <div className="solve-action-panel" aria-hidden="true">
                <div className="solve-action-panel-inner">
                  <h3 className="text-xl text-gold mb-4 text-center">Что мы делаем</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed text-left sm:text-justify">
                    {card.action}
                  </p>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </Section>
  );
}
