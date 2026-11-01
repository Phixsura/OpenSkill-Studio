import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOtelPanel } from "@/components/fleet-otel-panel";
describe("FleetOtelPanel", () => { it("renders", () => {
    const { container } = render(<FleetOtelPanel total={20} instrumented={16} auto={12} manual={4} coveragePct={80} mature={true} />);
    expect(container.textContent).toContain("OpenTelemetry");
    expect(container.textContent).toContain("80%");
}); });
