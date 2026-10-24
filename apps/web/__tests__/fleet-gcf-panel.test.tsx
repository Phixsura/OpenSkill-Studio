import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGcfPanel } from "@/components/fleet-gcf-panel";
describe("FleetGcfPanel", () => { it("renders", () => {
    const { container } = render(<FleetGcfPanel functions={30} active={30} executions={5000000} avgDuration={80} />);
    expect(container.textContent).toContain("Cloud Functions");
    expect(container.textContent).toContain("5,000,000");
}); });
