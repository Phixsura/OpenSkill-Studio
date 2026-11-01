import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetJaegerPanel } from "@/components/fleet-jaeger-panel";
describe("FleetJaegerPanel", () => { it("renders", () => {
    const { container } = render(<FleetJaegerPanel collectors={3} healthy={3} spansPerSec={30000} storageGb={500} allHealthy={true} />);
    expect(container.textContent).toContain("Jaeger");
    expect(container.textContent).toContain("30,000");
}); });
