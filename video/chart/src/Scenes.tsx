import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, BG, M, SANS, mono, ramp, rise, breathe, Kicker } from "./theme";

const Frame: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: BG, fontFamily: SANS, color: C.ink, ...breathe(f) }}>{children}</AbsoluteFill>
  );
};

// thin accent tick that draws in — the family's recurring mark
const Tick: React.FC<{ frame: number; at?: number; w?: number }> = ({ frame, at = 0, w = 64 }) => (
  <div style={{ width: w * ramp(frame, at, at + 12), height: 4, background: C.accent }} />
);

// ---- TitleCard: kicker + one strong line (s01 hook, s10 human) ----
export const TitleCard: React.FC<{ kicker: string; line: string }> = ({ kicker, line }) => {
  const f = useCurrentFrame();
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 430, width: 1500 }}>
        <Tick frame={f} at={2} />
        <div style={{ marginTop: 26 }}>
          <Kicker frame={f} text={kicker} at={8} />
        </div>
        <div style={{ fontSize: 86, fontWeight: 700, letterSpacing: -1.5, lineHeight: 1.05, marginTop: 18, ...rise(f, 16, 16) }}>
          {line}
        </div>
      </div>
    </Frame>
  );
};

// ---- StatPunch: one dominant figure + unit + sub (s02, s08, s13) ----
export const StatPunch: React.FC<{ stat: string; unit: string; sub: string }> = ({ stat, unit, sub }) => {
  const f = useCurrentFrame();
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 300, width: 1680 }}>
        <Kicker frame={f} text="COSTGUARD" at={2} />
        <div style={{ ...mono, fontSize: 300, fontWeight: 600, lineHeight: 0.86, color: C.accent, marginTop: 16, ...rise(f, 10, 18, 18) }}>
          {stat}
        </div>
        <div style={{ fontSize: 46, fontWeight: 600, marginTop: 20, ...rise(f, 28) }}>{unit}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 26, ...rise(f, 40) }}>
          <div style={{ width: 4, height: 30, background: C.line }} />
          <div style={{ fontSize: 28, color: C.body }}>{sub}</div>
        </div>
      </div>
    </Frame>
  );
};

// ---- NamedTask: a rule/command statement (s03) ----
export const NamedTask: React.FC<{ label: string; task: string }> = ({ label, task }) => {
  const f = useCurrentFrame();
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 388, width: 1500 }}>
        <Kicker frame={f} text={label.toUpperCase()} at={2} />
        <div style={{ display: "flex", gap: 26, marginTop: 28, ...rise(f, 12, 16) }}>
          <div style={{ width: 4, background: C.accent, alignSelf: "stretch" }} />
          <div style={{ ...mono, fontSize: 52, fontWeight: 500, lineHeight: 1.25, color: C.ink }}>{task}</div>
        </div>
      </div>
    </Frame>
  );
};

// ---- SplitScreen: one run vs twenty runs (s06) ----
type Item = { who: string; text: string; tone?: "ok" | "muted" | "warn" | "accent" };
const toneColor = (t?: string) => (t === "accent" ? C.accent : t === "ok" ? C.ok : t === "warn" ? C.body : C.muted);

export const SplitScreen: React.FC<{
  leftLabel: string; rightLabel: string; leftItems: Item[]; rightItems: Item[];
}> = ({ leftLabel, rightLabel, leftItems, rightItems }) => {
  const f = useCurrentFrame();
  const Col: React.FC<{ x: number; label: string; items: Item[]; at: number; dim?: boolean }> = ({ x, label, items, at, dim }) => (
    <div style={{ position: "absolute", left: x, top: 250, width: 640 }}>
      <div style={{ ...mono, fontSize: 20, letterSpacing: 3, color: dim ? C.muted : C.accent, ...rise(f, at) }}>{label.toUpperCase()}</div>
      <div style={{ marginTop: 36 }}>
        {items.map((it, i) => (
          <div key={i} style={{ marginBottom: 30, ...rise(f, at + 6 + i * 4) }}>
            <div style={{ fontSize: 20, color: C.muted, marginBottom: 6 }}>{it.who}</div>
            <div style={{ fontSize: 38, fontWeight: 600, color: toneColor(it.tone) }}>{it.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 120, fontSize: 40, fontWeight: 700, ...rise(f, 2) }}>
        Why run it twenty times?
      </div>
      <Col x={M} label={leftLabel} items={leftItems} at={14} dim />
      <div style={{ position: "absolute", left: 940, top: 250, width: 1, height: 520, background: C.line, opacity: ramp(f, 16, 30) }} />
      <Col x={1040} label={rightLabel} items={rightItems} at={22} />
    </Frame>
  );
};

// ---- Explain: what it does, in plain terms — 3 numbered steps (distinct rhythm) ----
export const Explain: React.FC = () => {
  const f = useCurrentFrame();
  const steps = [
    { n: "1", t: "Run the new agent", s: "on the same invoices, many times" },
    { n: "2", t: "Price each correct result", s: "dollars per correctly-done invoice" },
    { n: "3", t: "Block it if it got pricier", s: "same work, higher cost → stop" },
  ];
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 150 }}>
        <Kicker frame={f} text="WHAT COSTGUARD DOES" at={2} />
        <div style={{ fontSize: 62, fontWeight: 700, letterSpacing: -1, marginTop: 16, ...rise(f, 8) }}>
          A spend-checker for your agents
        </div>
      </div>
      {/* connector hairline that draws across the three steps */}
      <div style={{ position: "absolute", left: M + 30, top: 470, width: (1920 - 2 * M - 60) * ramp(f, 24, 70), height: 2, background: C.line }} />
      {steps.map((st, i) => {
        const x = M + i * 540;
        return (
          <div key={i} style={{ position: "absolute", left: x, top: 430, width: 470, ...rise(f, 26 + i * 10, 14) }}>
            <div style={{ width: 80, height: 80, borderRadius: 16, border: `2px solid ${C.accent}`, display: "flex", alignItems: "center", justifyContent: "center", background: BG }}>
              <span style={{ ...mono, fontSize: 40, fontWeight: 600, color: C.accent }}>{st.n}</span>
            </div>
            <div style={{ fontSize: 34, fontWeight: 600, marginTop: 28 }}>{st.t}</div>
            <div style={{ fontSize: 24, color: C.body, marginTop: 10, lineHeight: 1.3 }}>{st.s}</div>
          </div>
        );
      })}
    </Frame>
  );
};

// ---- Install: how to try it — a terminal block (different aesthetic on purpose) ----
export const Install: React.FC = () => {
  const f = useCurrentFrame();
  const lines = [
    { at: 24, p: "$", c: "git clone github.com/GHGuide/costguard" },
    { at: 44, p: "$", c: "python3 -m costguard.cli" },
  ];
  const cursorOn = Math.floor(f / 15) % 2 === 0;
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 150 }}>
        <Kicker frame={f} text="TRY IT — TWO COMMANDS" at={2} />
        <div style={{ fontSize: 62, fontWeight: 700, letterSpacing: -1, marginTop: 16, ...rise(f, 8) }}>
          Clone it. Run the gate.
        </div>
      </div>
      {/* terminal panel */}
      <div style={{ position: "absolute", left: M, top: 380, width: 1680, padding: "34px 40px", background: "#0a0e14", border: `1px solid ${C.line}`, borderRadius: 14, ...rise(f, 14, 16) }}>
        <div style={{ ...mono, fontSize: 16, color: C.muted, letterSpacing: 2, marginBottom: 22 }}>costguard — terminal</div>
        {lines.map((ln, i) => (
          <div key={i} style={{ ...mono, fontSize: 30, marginBottom: 18, opacity: ramp(f, ln.at, ln.at + 6) }}>
            <span style={{ color: C.accent, marginRight: 16 }}>{ln.p}</span>
            <span style={{ color: C.ink }}>{ln.c}</span>
            {i === lines.length - 1 && cursorOn ? <span style={{ color: C.accent }}> ▋</span> : null}
          </div>
        ))}
        {/* the verdict it prints */}
        <div style={{ ...mono, fontSize: 28, marginTop: 26, opacity: ramp(f, 70, 80) }}>
          <span style={{ color: C.muted }}>VERDICT  </span>
          <span style={{ color: C.fail, fontWeight: 600 }}>FAIL · block</span>
          <span style={{ color: C.muted }}>   cost/invoice </span>
          <span style={{ color: C.accent }}>7.27×</span>
        </div>
      </div>
      <div style={{ position: "absolute", left: M, top: 760, fontSize: 26, color: C.body, ...rise(f, 88) }}>
        point it at your own agent by editing two lines.
      </div>
    </Frame>
  );
};

// ---- Architecture: the gate flow, dark + on-brand (replaces the light screenshot) ----
const Node: React.FC<{ x: number; y: number; w: number; title: string; sub?: string; color?: string; frame: number; at: number; strong?: boolean }> =
  ({ x, y, w, title, sub, color, frame, at, strong }) => (
    <div style={{ position: "absolute", left: x, top: y, width: w, padding: "14px 22px", borderRadius: 12, background: "#10151d", border: `${strong ? 2 : 1}px solid ${color || C.line}`, ...rise(frame, at, 10) }}>
      <div style={{ fontSize: 25, fontWeight: 600, color: C.ink }}>{title}</div>
      {sub ? <div style={{ fontSize: 17, color: C.muted, marginTop: 5 }}>{sub}</div> : null}
    </div>
  );
const VLine: React.FC<{ x: number; y: number; h: number; frame: number; at: number }> = ({ x, y, h, frame, at }) => (
  <div style={{ position: "absolute", left: x, top: y, width: 2, height: h * ramp(frame, at, at + 8), background: C.line }} />
);

export const Architecture: React.FC = () => {
  const f = useCurrentFrame();
  const cx = 680, w = 560;
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 78 }}>
        <Kicker frame={f} text="ARCHITECTURE" at={2} />
        <div style={{ fontSize: 50, fontWeight: 700, letterSpacing: -0.5, marginTop: 12, ...rise(f, 8) }}>How the gate works</div>
      </div>
      <Node frame={f} at={16} x={cx} y={188} w={w} title="A developer changes the agent" sub="new prompt · model · tool" />
      <VLine frame={f} at={22} x={cx + w / 2} y={250} h={30} />
      <Node frame={f} at={26} x={cx} y={282} w={w} title="Agent under test" sub="UiPath Document Understanding — or LangChain / CrewAI" />
      <VLine frame={f} at={32} x={cx + w / 2} y={356} h={30} />
      <Node frame={f} at={36} x={cx} y={388} w={w} color={C.accent} strong title="CostGuard coded agent" sub="runs it N times · cost per correct outcome + CI · vs last green baseline" />
      <VLine frame={f} at={44} x={cx + w / 2} y={470} h={28} />
      <Node frame={f} at={48} x={cx + 70} y={500} w={w - 140} title="Verdict" sub="cost-per-outcome vs baseline" />
      {/* distributor to three outcomes */}
      <VLine frame={f} at={56} x={cx + w / 2} y={566} h={24} />
      <div style={{ position: "absolute", left: 360, top: 590, width: 1200, height: 2, background: C.line, opacity: ramp(f, 58, 68) }} />
      <Node frame={f} at={62} x={360} y={612} w={350} color={C.ok} title="PASS → promote" sub="ship the new version" />
      <Node frame={f} at={68} x={760} y={612} w={350} color={C.accent} title="FAIL → block" sub="stop the regression" />
      <Node frame={f} at={74} x={1160} y={612} w={400} color="#cf9a3b" title="NEEDS_REVIEW" sub="→ a human in Action Center" />
      {/* platform footer band */}
      <div style={{ position: "absolute", left: 360, top: 760, width: 1200, padding: "18px 26px", borderRadius: 12, background: "#0c1118", border: `1px solid ${C.line}`, ...rise(f, 82) }}>
        <div style={{ ...mono, fontSize: 19, color: C.body, letterSpacing: 0.5 }}>
          Runs on UiPath Automation Cloud — serverless job · registers a Test Cloud result · governed by the AI Trust Layer
        </div>
      </div>
    </Frame>
  );
};

// ---- GreenRed: the killer moment — passes every test, still 7x more ----
export const GreenRed: React.FC = () => {
  const f = useCurrentFrame();
  const checks = [
    "Fields extracted correctly",
    "Schema valid",
    "Accuracy 100%",
    "Correctness QA passed",
  ];
  const Check: React.FC<{ y: number; label: string; at: number }> = ({ y, label, at }) => {
    const on = ramp(f, at, at + 8);
    return (
      <div style={{ position: "absolute", left: M, top: y, display: "flex", alignItems: "center", gap: 18, opacity: on }}>
        <div style={{ width: 34, height: 34, borderRadius: 8, border: `2px solid ${C.ok}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ color: C.ok, fontSize: 22, fontWeight: 700, lineHeight: 1 }}>✓</span>
        </div>
        <span style={{ fontSize: 30, color: C.ink }}>{label}</span>
      </div>
    );
  };
  const gate = ramp(f, 150, 168); // the flip to red
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 96 }}>
        <Kicker frame={f} text="THE TRAP, SHOWN" at={2} />
        <div style={{ fontSize: 56, fontWeight: 700, letterSpacing: -1, marginTop: 14, ...rise(f, 8) }}>
          It passes every test you already have
        </div>
      </div>
      {/* left: the correctness suite, all green */}
      {checks.map((c, i) => <Check key={i} y={250 + i * 78} label={c} at={20 + i * 14} />)}
      <div style={{ position: "absolute", left: M, top: 250 + 4 * 78 + 10, ...mono, fontSize: 22, color: C.ok, letterSpacing: 1, opacity: ramp(f, 90, 100) }}>
        YOUR SUITE: PASS — would ship
      </div>
      {/* divider */}
      <div style={{ position: "absolute", left: 880, top: 250, width: 1, height: 430, background: C.line, opacity: ramp(f, 16, 30) }} />
      {/* right: CostGuard flips it red */}
      <div style={{ position: "absolute", left: 980, top: 250, width: 760, opacity: ramp(f, 120, 134) }}>
        <div style={{ ...mono, fontSize: 20, letterSpacing: 2, color: C.muted }}>COSTGUARD — COST PER CORRECT INVOICE</div>
        <div style={{ ...mono, fontSize: 150, fontWeight: 600, lineHeight: 1, color: C.fail, marginTop: 10, transform: `scale(${0.85 + 0.15 * gate})` }}>7.27×</div>
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 22 }}>
          <div style={{ width: 4, height: 42, background: C.fail }} />
          <div style={{ ...mono, fontSize: 34, fontWeight: 600, color: C.fail }}>FAIL — BLOCKED</div>
        </div>
        <div style={{ fontSize: 26, color: C.body, marginTop: 16 }}>same answers, 7× the bill</div>
      </div>
      {/* punch line */}
      <div style={{ position: "absolute", left: M, top: 740, fontSize: 34, fontWeight: 600, color: C.ink, ...rise(f, 200, 12) }}>
        Every test you have said ship it. The bill said 7× more.
      </div>
    </Frame>
  );
};

// ---- LogoCta: wordmark + url (s14) ----
export const LogoCta: React.FC<{ cta: string }> = ({ cta }) => {
  const f = useCurrentFrame();
  return (
    <Frame>
      <div style={{ position: "absolute", left: M, top: 452, width: 1500 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, ...rise(f, 4, 14) }}>
          {/* minimal gate mark */}
          <div style={{ width: 46, height: 46, border: `4px solid ${C.accent}`, borderRadius: 10, position: "relative" }}>
            <div style={{ position: "absolute", left: 8, top: 19, width: 26, height: 4, background: C.accent }} />
          </div>
          <div style={{ fontSize: 76, fontWeight: 700, letterSpacing: -1 }}>CostGuard</div>
        </div>
        <div style={{ fontSize: 32, color: C.body, marginTop: 24, ...rise(f, 16) }}>
          a cost gate for your agents — built and run on UiPath
        </div>
        <div style={{ ...mono, fontSize: 26, color: C.accent, marginTop: 30, ...rise(f, 26) }}>{cta}</div>
      </div>
    </Frame>
  );
};
