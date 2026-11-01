import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIHealthScoreCard from "../src/components/api-health-score-card";

const dimensions = [
  { dimension_id: "uptime", name: "Uptime", weight: 3, score: 99.5 },
  { dimension_id: "latency", name: "Latency", weight: 1, score: 85 },
];

describe("APIHealthScoreCard", () => {
  it("renders composite score", () => {
    const { container } = render(<APIHealthScoreCard dimensions={dimensions} compositeScore={95.9} appName="App" />);
    expect(container.textContent).toContain("Health Score");
    expect(container.textContent).toContain("95.9");
  });

  it("shows dimensions with scores", () => {
    const { container } = render(<APIHealthScoreCard dimensions={dimensions} compositeScore={95} appName="App" />);
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("99.5/100");
    expect(container.textContent).toContain("w3");
  });

  it("shows empty state", () => {
    const { container } = render(<APIHealthScoreCard dimensions={[]} compositeScore={100} appName="App" />);
    expect(container.textContent).toContain("No health dimensions");
  });
});
