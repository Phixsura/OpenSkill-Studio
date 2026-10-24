import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTelemetryV3Panel } from "@/components/fleet-ai-telemetry-v3-panel";
describe("FleetAiTelemetryV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiTelemetryV3Panel collectors={5} active={5} metrics={5000000000} traces={2000000000} logs={20000000000} storage={100000} />);
    expect(container.textContent).toContain("Telemetry v3");
}); });
