import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetScaffolderPanel } from "@/components/fleet-scaffolder-panel";
describe("FleetScaffolderPanel", () => { it("renders", () => {
    const { container } = render(<FleetScaffolderPanel templates={15} executions={200} topTemplate="service-template" />);
    expect(container.textContent).toContain("Scaffolder");
    expect(container.textContent).toContain("service-template");
}); });
