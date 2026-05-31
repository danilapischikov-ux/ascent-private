import { useState } from "react";
import { Section } from "./Section";
import audienceImage from "../../../Кому подходим.png";

const items = [
  {
    title: "Инвесторы с капиталом от $50,000",
    text: "Ascent Private помогает таким инвесторам смотреть на рынок через структуру: сценарии, риск-менеджмент, волатильность, ликвидность, вероятности и ограничения. Это не формат “куда вложить деньги прямо сейчас”, а способ повысить качество мышления перед принятием решений.",
    criteria: [
      "У вас есть капитал, который требует профессионального отношения",
      "Вы понимаете, что доходность не существует отдельно от риска",
      "Вы не хотите действовать на основе рыночного шума",
      "Вы готовы принимать решения самостоятельно",
    ],
  },
  {
    title: "Предприниматели и собственники бизнеса",
    text: "У предпринимателей часто нет времени ежедневно следить за рынком, разбирать опционы, изучать волатильность и строить сценарные модели. Ascent Private помогает перевести рынок на язык, близкий предпринимателю: риск, вероятность, капитал, сценарий, ограничение, эффективность.",
    criteria: [
      "Вы привыкли принимать решения на основе данных",
      "Вы цените время и не хотите становиться трейдером",
      "Вы хотите отделить инвестиционную систему от эмоций",
      "Вам нужен второй профессиональный взгляд",
    ],
  },
  {
    title: "Опытные частные инвесторы",
    text: "Ascent Private подходит опытным частным инвесторам как дополнительный профессиональный аналитический слой. Мы не объясняем рынок “с нуля”, а помогаем глубже понимать идеи, особенно если они связаны с опционами, волатильностью, вероятностными сценариями и контролем риска.",
    criteria: [
      "У вас уже есть опыт самостоятельных инвестиций",
      "Вы сталкивались с ограничениями собственного подхода",
      "Вам интересны более сложные инструменты",
      "Вы хотите перейти от набора сделок к системе",
    ],
  },
  {
    title: "Топ-менеджеры",
    text: "Топ-менеджеры и высокооплачиваемые специалисты не всегда хотят глубоко погружаться в рынок самостоятельно, но хотят понимать, что происходит с капиталом, какие есть возможности, какие риски и где заканчивается разумная инвестиционная логика. Ascent Private даёт структурированную аналитику без избыточного шума и без давления.",
    criteria: [
      "У вас есть капитал, но нет времени на ежедневный анализ рынка",
      "Вам важно принимать решения без давления",
      "Вы цените ясность и структурность",
      "Вы встраиваете инвестиции в свою финансовую архитектуру.",
    ],
  },
  {
    title: "Инвесторы, которым важен контроль риска",
    text: "Философия обязательного контроля риска подходит инвесторам, которые не хотят слепо гнаться за доходностью и понимают, что крупный капитал требует аккуратности. Особенно это важно при работе с опционами, где риск зависит не только от направления цены, но и от времени, волатильности, ликвидности и структуры позиции.",
    criteria: [
      "Вы хотите видеть риск до принятия решения",
      "Вы не воспринимаете риск как абстрактное предупреждение",
      "Вы готовы отказаться от идеи, если риск неадекватен",
      "Вы хотите иметь сценарный план",
    ],
  },
  {
    title: "Профессиональные трейдеры",
    text: "Профессиональные трейдеры уже умеют работать с рынком, и именно поэтому им важна не поверхностная аналитика, а качественный внешний контур проверки идей. Наш формат особенно полезен, когда трейдеру нужно не больше мнений, а более точная рамка для оценки структуры позиции.",
    criteria: [
      "Вы работаете с опционами или хотите глубже их понимать",
      "Вам важна проверка гипотез, а не готовые сигналы",
      "У вас уже есть система, которую хотите усилить",
      "Вам полезен внешний профессиональный взгляд",
    ],
  },
  {
    title: "Инвесторы, интересующиеся рынком США",
    text: "Ascent Private подходит инвесторам, которые хотят понимать американский рынок не на уровне заголовков, а через более глубокую аналитику: ликвидность, implied volatility, expected move, сценарии, риск-профиль и структуру стратегий. Интересуются биржевыми опционами и их возможностями.",
    criteria: [
      "Вам интересны международные рынки",
      "Вы понимаете, что опционы требуют подготовки",
      "Вам нужна аналитика по сложным рыночным ситуациям",
      "Вы хотите видеть связь между идеей и структурой риска",
    ],
  },
  {
    title: "Инвесторы, уставшие от банковских шаблонов и массовых продуктов",
    text: "Ascent Private подходит тем, кто хочет более интеллектуальный и персонализированный аналитический подход. Не массовую витрину продуктов, а частный формат, где в центре внимания — логика, риск, сценарии и качество понимания рынка.",
    criteria: [
      "Вам недостаточно стандартных инвестиционных продуктов",
      "Вы не хотите быть частью массовой воронки",
      "Вы цените независимость мышления",
      "Вы хотите видеть не только продукт, а также систему анализа",
    ],
  },
  {
    title: "Финансовые аналитики",
    text: "Финансовые аналитики умеют работать с данными, отчётностью, мультипликаторами, макрофакторами и рыночными ожиданиями. Но при анализе рынка США и особенно опционных стратегий одной фундаментальной или макроэкономической логики часто недостаточно.",
    criteria: [
      "Вам интересны опционы как источник рыночных ожиданий",
      "Вы работаете с решениями, где цена ошибки высока",
      "Вы цените строгую и проверяемую аргументацию",
      "Вы хотите усилить аналитику через сценарии",
    ],
  },
  {
    title: "Инвесторы, которые хотят принимать решения спокойнее",
    text: "Ascent Private помогает создать более спокойный подход к рынку через сценарное мышление. Когда инвестор заранее понимает возможные варианты развития событий, он меньше зависит от эмоций и лучше видит границы рационального решения.",
    criteria: [
      "Вы замечали влияние эмоций на свои решения",
      "Вам важно заранее понимать сценарии",
      "Вы хотите снизить зависимость от новостей",
      "Вы хотите больше финансовой дисциплины",
    ],
  },
];

type AudienceItem = (typeof items)[number];

function AudienceCard({
  item,
  index,
  className = "",
  onSelect,
}: {
  item: AudienceItem;
  index: number;
  className?: string;
  onSelect?: () => void;
}) {
  return (
    <article
      className={`ascent-card audience-marquee-card visual-mark bg-card/62 backdrop-blur-md p-5 sm:p-6 md:p-8 ${className}`}
      role={onSelect ? "button" : undefined}
      tabIndex={onSelect ? 0 : undefined}
      onClick={onSelect}
      onKeyDown={(event) => {
        if (!onSelect || (event.key !== "Enter" && event.key !== " ")) return;

        event.preventDefault();
        onSelect();
      }}
    >
      <div className="flex flex-col sm:flex-row items-start gap-4 sm:gap-5">
        <span className="size-11 sm:size-12 border border-gold-soft text-gold text-xs tracking-[0.18em] flex items-center justify-center shrink-0">
          {String(index + 1).padStart(2, "0")}
        </span>
        <div>
          <h3 className="text-[1.55rem] sm:text-2xl text-gold leading-tight mb-4">{item.title}</h3>
          <p className="text-sm text-muted-foreground leading-relaxed text-left sm:text-justify">
            {item.text}
          </p>
          <h3 className="mt-6 text-xl text-gold mb-3">Критерии, по которым вы нам подходите</h3>
          <ul className="space-y-2">
            {item.criteria.map((criterion) => (
              <li
                key={criterion}
                className="flex items-start gap-3 text-sm text-muted-foreground leading-relaxed"
              >
                <span className="mt-2 size-1.5 bg-gold rounded-full shrink-0" />
                <span>{criterion}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </article>
  );
}

export function Audience() {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const selectedItem = selectedIndex === null ? null : items[selectedIndex];

  return (
    <Section
      id="audience"
      image={audienceImage}
      imagePosition="center right"
      eyebrow="Кому подходим"
      title={
        <>
          Кому подходит <span className="text-gold italic">Ascent Private</span>
        </>
      }
      subtitle="Ascent Private подходит инвесторам, которые уже воспринимают капитал как систему, а не как набор случайных сделок. Мы работаем с теми, кому важно понимать рынок глубже: видеть не только потенциальную доходность, но и риск, сценарии, ограничения, волатильность и логику принятия решений."
    >
      <div
        className="audience-marquee reveal reveal-delay-1"
        data-selected={selectedIndex !== null}
        onMouseLeave={() => setSelectedIndex(null)}
      >
        <div className="audience-marquee-track">
          {[0, 1].map((loopIndex) => (
            <div key={loopIndex} className="audience-marquee-group" aria-hidden={loopIndex === 1}>
              {items.map((item, index) => (
                <AudienceCard
                  key={`${loopIndex}-${item.title}`}
                  item={item}
                  index={index}
                  onSelect={() => setSelectedIndex(index)}
                />
              ))}
            </div>
          ))}
        </div>

        {selectedItem && selectedIndex !== null && (
          <div className="audience-marquee-focus">
            <AudienceCard
              item={selectedItem}
              index={selectedIndex}
              className="audience-marquee-card-focused"
              onSelect={() => setSelectedIndex((selectedIndex + 1) % items.length)}
            />
          </div>
        )}
      </div>

      <div className="ascent-card mt-8 sm:mt-12 bg-background/62 backdrop-blur-md p-6 sm:p-7 md:p-10 text-center reveal reveal-delay-2">
        <div className="mx-auto flex max-w-4xl flex-col items-center gap-6 sm:gap-7">
          <p className="text-xs uppercase tracking-[0.24em] text-gold">
            Не уверены, подходит ли вам формат Ascent Private?
          </p>
          <p
            className="text-xl md:text-2xl text-foreground leading-snug"
            style={{ fontFamily: "var(--font-display)", fontWeight: 500, letterSpacing: 0 }}
          >
            Начните с ознакомительного периода. В течение месяца вы получаете доступ к закрытой
            аналитической среде. Наблюдаете, оцениваете, используете. Далее, принимаете решение на
            сколько подходит вам сервис.
          </p>
          <a
            href="https://t.me/+qAf6qjG9MbFiMGVi"
            className="ascent-button text-primary-foreground bg-gradient-gold shadow-gold"
          >
            Получить доступ
          </a>
        </div>
      </div>
    </Section>
  );
}
