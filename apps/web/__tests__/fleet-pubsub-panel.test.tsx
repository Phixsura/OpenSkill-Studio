import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPubsubPanel } from "@/components/fleet-pubsub-panel";
describe("FleetPubsubPanel", () => { it("renders", () => {
    const { container } = render(<FleetPubsubPanel topics={50} messages={20000000} subscriptions={100} backlog={500} />);
    expect(container.textContent).toContain("Pub/Sub");
    expect(container.textContent).toContain("20,000,000");
}); });
