import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSaasMetricsPanel } from "@/components/fleet-ai-saas-metrics-panel";
describe("FleetAiSaasMetricsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSaasMetricsPanel trackers={2} active={2} arr={100000000} ltv={100000} cac={8000} ltvCac={12.5} />);
    expect(container.textContent).toContain("SaaS Metrics");
}); });
