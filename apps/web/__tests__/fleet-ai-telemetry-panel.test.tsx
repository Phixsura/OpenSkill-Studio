import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTelemetryPanel } from "@/components/fleet-ai-telemetry-panel";
describe("FleetAiTelemetryPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTelemetryPanel collectors={8} active={8} metrics={500000000} traces={200000000} logs={2000000000} />);
    expect(container.textContent).toContain("AI Telemetry");
}); });
