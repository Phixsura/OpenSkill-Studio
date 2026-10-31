import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperScoreBadge } from "@/components/developer-score-badge";

describe("DeveloperScoreBadge", () => {
  it("renders", () => {
    const breakdown = { apps_published: 150, total_installs: 50, avg_rating: 96 };
    const { container } = render(
      <DeveloperScoreBadge score={650} maxScore={1000} tier="expert"
        percentile={65} breakdown={breakdown} />
    );
    expect(container.textContent).toContain("650");
    expect(container.textContent).toContain("🌟");
    expect(container.textContent).toContain("expert");
    expect(container.textContent).toContain("Top 65%");
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("Installs");
  });
});
