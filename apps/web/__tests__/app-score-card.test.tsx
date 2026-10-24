import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppScoreCard } from "@/components/app-score-card";

describe("AppScoreCard", () => {
  it("renders", () => {
    const criteria = { description_quality: 18, screenshots: 15, documentation: 10,
      testing: 10, rating: 19, installs: 10, update_frequency: 10, support: 5 };
    const { container } = render(
      <AppScoreCard score={97} grade="A+" criteria={criteria} improvements={[]} />
    );
    expect(container.textContent).toContain("A+");
    expect(container.textContent).toContain("97/100");
    expect(container.textContent).toContain("Description");
    expect(container.textContent).toContain("Screenshots");
  });
  it("shows improvements", () => {
    const { container } = render(
      <AppScoreCard score={30} grade="D" criteria={{ testing: 0, documentation: 0 }}
        improvements={["testing", "documentation"]} />
    );
    expect(container.textContent).toContain("💡 Improve:");
    expect(container.textContent).toContain("Tests");
    expect(container.textContent).toContain("Docs");
  });
});
