import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSqsPanel } from "@/components/fleet-sqs-panel";
describe("FleetSqsPanel", () => { it("renders", () => {
    const { container } = render(<FleetSqsPanel queues={30} visible={500} inFlight={200} dlqMessages={10} />);
    expect(container.textContent).toContain("SQS");
    expect(container.textContent).toContain("10 DLQ");
}); });
