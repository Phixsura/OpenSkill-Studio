import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperSatisfactionCard from "../src/components/api-developer-satisfaction-card";

const sat = { nps_score: 70, csat_score: 4.5, total_responses: 200, promoters: 150, passives: 30, detractors: 20, sentiment: "excellent" };

describe("APIDeveloperSatisfactionCard", () => {
  it("shows satisfaction", () => {
    const { container } = render(<APIDeveloperSatisfactionCard satisfaction={sat} appName="App" />);
    expect(container.textContent).toContain("Dev Satisfaction");
    expect(container.textContent).toContain("70");
    expect(container.textContent).toContain("4.5/5");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("150");
  });
});
