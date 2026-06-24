import React from "react";
import { Composition } from "remotion";
import { CostRegression } from "./CostRegression";

// 10s @ 30fps = 300 frames, 1080p — matches video.config.json.
export const RemotionRoot: React.FC = () => (
  <Composition
    id="CostRegression"
    component={CostRegression}
    durationInFrames={300}
    fps={30}
    width={1920}
    height={1080}
  />
);
