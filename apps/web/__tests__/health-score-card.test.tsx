import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HealthScoreCard from "../src/components/health-score-card";

const signals = [
  { name: "uptime", value: 99.95, score: 99.95, status: "ok" as const },
  { name: "error_rate", value: 2, score: 80, status: "degraded" as const },
  { name: "latency", value: 150, score: 85, status: "ok" as const },
  { name: "saturation", value: 75, score: 25, status: "degraded" as const },
];

describe("HealthScoreCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <HealthScoreCard overallScore={85} grade="B" signals={signals} appName="My App" />,
    );
    expect(container.textContent).toContain("Health Score");
    expect(container.textContent).toContain("My App");
  });

  it("shows grade and score", () => {
    const { container } = render(
      <HealthScoreCard overallScore={85} grade="B" signals={signals} appName="App" />,
    );
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("85/100");
  });

  it("renders signal names", () => {
    const { container } = render(
      <HealthScoreCard overallScore={85} grade="B" signals={signals} appName="App" />,
    );
    expect(container.textContent).toContain("uptime");
    expect(container.textContent).toContain("error rate");
    expect(container.textContent).toContain("latency");
  });

  it("shows signal scores", () => {
    const { container } = render(
      <HealthScoreCard overallScore={85} grade="B" signals={signals} appName="App" />,
    );
    expect(container.textContent).toContain("100"); // uptime rounded
    expect(container.textContent).toContain("80");
  });

  it("renders different grades", () => {
    const { container } = render(
      <HealthScoreCard overallScore={50} grade="F" signals={signals} appName="App" />,
    );
    expect(container.textContent).toContain("F");
  });
});
