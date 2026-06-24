import React from "react";
import { Composition } from "remotion";
import { CostRegression } from "./CostRegression";
import { TitleCard, StatPunch, NamedTask, SplitScreen, LogoCta } from "./Scenes";

const base = { fps: 30, width: 1920, height: 1080 } as const;

export const RemotionRoot: React.FC = () => (
  <>
    {/* hero data scene — live UiPath run (README/teaser) */}
    <Composition id="CostRegression" component={CostRegression} durationInFrames={300} {...base} />

    {/* narrated variant for the master at s07 — the 7.27x demo run the VO describes */}
    <Composition id="CostRegression7" component={CostRegression} durationInFrames={300} {...base}
      defaultProps={{
        baseCps: 0.0009, candCps: 0.006543, ratio: 7.27, accDelta: 4.4,
        factors: [
          { name: "model price", mult: 3.0 },
          { name: "verify pass", mult: 2.0 },
          { name: "token volume", mult: 1.21 },
        ],
        kicker: "COSTGUARD — COST-REGRESSION GATE",
        footer: "20 deterministic runs · cost per correctly-processed invoice",
      }} />

    {/* s01 hook */}
    <Composition id="s01-hook" component={TitleCard} durationInFrames={150} {...base}
      defaultProps={{ kicker: "COSTGUARD", line: "It passed the tests. It still cost 7× more." }} />

    {/* s02 the gap */}
    <Composition id="s02-gap" component={StatPunch} durationInFrames={150} {...base}
      defaultProps={{ stat: "0", unit: "gates for agent cost", sub: "correctness is tested — cost isn’t" }} />

    {/* s03 name the gate */}
    <Composition id="s03-name" component={NamedTask} durationInFrames={150} {...base}
      defaultProps={{ label: "The gate", task: "Block this agent version if it costs more per processed invoice" }} />

    {/* s06 one run vs twenty */}
    <Composition id="s06-contrast" component={SplitScreen} durationInFrames={210} {...base}
      defaultProps={{
        leftLabel: "One run", rightLabel: "Twenty runs",
        leftItems: [
          { who: "Quality", text: "looks fine", tone: "ok" },
          { who: "Cost", text: "no signal yet", tone: "muted" },
          { who: "Verdict", text: "would pass", tone: "warn" },
        ],
        rightItems: [
          { who: "Quality", text: "+4.4% accuracy", tone: "ok" },
          { who: "Cost", text: "7.27× per invoice", tone: "accent" },
          { who: "Verdict", text: "FAIL — blocked", tone: "accent" },
        ],
      }} />

    {/* s08 on uipath */}
    <Composition id="s08-uipath" component={StatPunch} durationInFrames={150} {...base}
      defaultProps={{ stat: "FAIL", unit: "action: block", sub: "real output of an unattended UiPath job (serverless)" }} />

    {/* s10 human in the loop */}
    <Composition id="s10-human" component={TitleCard} durationInFrames={150} {...base}
      defaultProps={{ kicker: "HUMAN IN THE LOOP", line: "Ship it anyway, or quarantine." }} />

    {/* s13 impact */}
    <Composition id="s13-impact" component={StatPunch} durationInFrames={150} {...base}
      defaultProps={{ stat: "7.27×", unit: "cost regression caught", sub: "blocked before production" }} />

    {/* s14 logo / cta */}
    <Composition id="s14-logo" component={LogoCta} durationInFrames={150} {...base}
      defaultProps={{ cta: "github.com/GHGuide/costguard" }} />
  </>
);
