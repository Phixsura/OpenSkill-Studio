import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLogAggPanel } from "@/components/fleet-ai-log-agg-panel";
describe("FleetAiLogAggPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLogAggPanel aggregators={3} active={3} logs={2000000000} storageGb={10000} sources={500} />);
    expect(container.textContent).toContain("Log Aggregator");
}); });
