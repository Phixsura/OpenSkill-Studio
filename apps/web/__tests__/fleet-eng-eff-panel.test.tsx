import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEngEffPanel } from "@/components/fleet-eng-eff-panel";
describe("FleetEngEffPanel", () => { it("renders", () => {
    const { container } = render(<FleetEngEffPanel velocity={80} quality={90} delivery={70} score={80} effective={true} />);
    expect(container.textContent).toContain("Engineering Effectiveness");
    expect(container.textContent).toContain("80%");
}); });
