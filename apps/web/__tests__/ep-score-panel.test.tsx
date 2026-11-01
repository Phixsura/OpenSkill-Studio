import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpScorePanel } from "@/components/ep-score-panel";
describe("EpScorePanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpScorePanel endpoints={[
        { endpoint: "/api/users", score: 95, grade: "A" },
        { endpoint: "/api/orders", score: 65, grade: "C" },
      ]} />
    );
    expect(container.textContent).toContain("Endpoint Scores");
    expect(container.textContent).toContain("2 endpoints");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("C");
  });
});
