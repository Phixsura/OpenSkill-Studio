import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAzureFuncPanel } from "@/components/fleet-azure-func-panel";
describe("FleetAzureFuncPanel", () => { it("renders", () => {
    const { container } = render(<FleetAzureFuncPanel apps={20} running={20} executions={8000000} gbSeconds={100000} />);
    expect(container.textContent).toContain("Azure Functions");
    expect(container.textContent).toContain("8,000,000");
}); });
