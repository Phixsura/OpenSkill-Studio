import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HealthScoreCard from "../src/components/api-developer-platform-sdk-consumer-api-health-score-card";

describe("HealthScoreCard", () => {
  it("renders title and endpoints", () => {
    const { container } = render(<HealthScoreCard />);
    expect(container.textContent).toContain("Health Score");
    expect(container.textContent).toContain("ep-auth");
    expect(container.textContent).toContain("ep-legacy");
  });

  it("shows grades and average", () => {
    const { container } = render(<HealthScoreCard />);
    expect(container.textContent).toContain("97.5");
    expect(container.textContent).toContain("3 endpoints scored");
  });
});
