import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-quota-rollover-card";

describe("ConsumerQuotaRolloverCard", () => {
  it("shows periods with rollover", () => {
    const periods = [
      { id: "Jan", base: 1000, used: 800, rolledIn: 0, rolledOut: 200 },
      { id: "Feb", base: 1000, used: 300, rolledIn: 200, rolledOut: 0 },
    ];
    const { container } = render(<Card consumerId="c1" periods={periods} maxRolloverPct={0.2} appName="App" />);
    expect(container.textContent).toContain("Quota Rollover");
    expect(container.textContent).toContain("Jan");
    expect(container.textContent).toContain("Feb");
    expect(container.textContent).toContain("+200 in");
    expect(container.textContent).toContain("-200 out");
    expect(container.textContent).toContain("20%");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumerId="c1" periods={[]} maxRolloverPct={0.2} appName="App" />);
    expect(container.textContent).toContain("No periods");
  });
});
