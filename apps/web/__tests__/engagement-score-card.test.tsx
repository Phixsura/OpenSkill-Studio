import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EngagementScoreCard } from "@/components/engagement-score-card";

describe("EngagementScoreCard", () => {
  it("renders score", () => {
    const { container } = render(
      <EngagementScoreCard score={85} tier="power" dauMau={80} featureAdoption={90} apiIntensity={75} />
    );
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("power");
    expect(container.textContent).toContain("80%");
  });
  it("shows casual", () => {
    const { container } = render(
      <EngagementScoreCard score={15} tier="casual" dauMau={5} featureAdoption={10} apiIntensity={20} />
    );
    expect(container.textContent).toContain("casual");
  });
});
