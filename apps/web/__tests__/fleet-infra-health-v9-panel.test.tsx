import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetInfraHealthV9Panel } from "@/components/fleet-infra-health-v9-panel";
describe("FleetInfraHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetInfraHealthV9Panel components={100} score={100} />);
    expect(container.textContent).toContain("Infra Health v9");
}); });
