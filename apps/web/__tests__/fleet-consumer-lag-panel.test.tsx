import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConsumerLagPanel } from "@/components/fleet-consumer-lag-panel";
describe("FleetConsumerLagPanel", () => { it("renders", () => {
    const { container } = render(<FleetConsumerLagPanel groups={5} totalLag={15500} maxLag={15000} behind={1} caughtUp={false} />);
    expect(container.textContent).toContain("Consumer Lag");
    expect(container.textContent).toContain("1 groups behind");
}); });
