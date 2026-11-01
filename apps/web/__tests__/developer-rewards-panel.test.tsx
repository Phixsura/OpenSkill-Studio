import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperRewardsPanel } from "@/components/developer-rewards-panel";

describe("DeveloperRewardsPanel", () => {
  it("renders rewards", () => {
    const { container } = render(
      <DeveloperRewardsPanel level="Builder" icon="🔨" totalPoints={450}
        nextLevel={{ name: "Expert", points_needed: 150 }} badges={["🚀", "⭐"]} />
    );
    expect(container.textContent).toContain("Builder");
    expect(container.textContent).toContain("450");
    expect(container.textContent).toContain("150 points to Expert");
    expect(container.textContent).toContain("🚀");
  });
  it("no next level at max", () => {
    const { container } = render(
      <DeveloperRewardsPanel level="Master" icon="👑" totalPoints={1500} nextLevel={null} badges={[]} />
    );
    expect(container.textContent).toContain("Master");
    expect(container.textContent).not.toContain("points to");
  });
});
