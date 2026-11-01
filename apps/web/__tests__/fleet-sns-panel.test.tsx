import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSnsPanel } from "@/components/fleet-sns-panel";
describe("FleetSnsPanel", () => { it("renders", () => {
    const { container } = render(<FleetSnsPanel topics={20} messages={5000000} subscriptions={100} failedDeliveries={0} />);
    expect(container.textContent).toContain("SNS");
    expect(container.textContent).toContain("5,000,000");
}); });
