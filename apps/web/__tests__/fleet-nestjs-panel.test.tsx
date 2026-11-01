import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNestjsPanel } from "@/components/fleet-nestjs-panel";
describe("FleetNestjsPanel", () => { it("renders", () => {
    const { container } = render(<FleetNestjsPanel apps={5} running={5} modules={100} endpoints={500} />);
    expect(container.textContent).toContain("NestJS");
    expect(container.textContent).toContain("500 endpoints");
}); });
