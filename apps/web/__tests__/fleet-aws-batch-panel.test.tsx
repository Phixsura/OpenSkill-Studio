import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAwsBatchPanel } from "@/components/fleet-aws-batch-panel";
describe("FleetAwsBatchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAwsBatchPanel queues={5} active={5} submitted={200} running={100} succeeded={1000} />);
    expect(container.textContent).toContain("AWS Batch");
}); });
