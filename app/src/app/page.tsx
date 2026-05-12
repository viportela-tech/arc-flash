const serviceCards = [
  {
    title: "Fase 0",
    description: "Ambiente Docker local para app, banco, storage, e-mail e worker."
  },
  {
    title: "Calculo",
    description: "Motor deterministico, versionado e validado por engenheiro habilitado."
  },
  {
    title: "Relatorios",
    description: "PDF com memorial de calculo, entradas, resultados, anexos e revisao tecnica."
  }
];

export default function Home() {
  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">ArcFlash MVP</p>
        <h1>Base local para desenvolvimento da ferramenta de arc flash</h1>
        <p>
          Scaffold inicial para construir o SaaS com projetos salvos, anexos,
          relatorios e calculo auditavel.
        </p>
      </section>

      <section className="grid" aria-label="Blocos iniciais">
        {serviceCards.map((card) => (
          <article className="card" key={card.title}>
            <h2>{card.title}</h2>
            <p>{card.description}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
