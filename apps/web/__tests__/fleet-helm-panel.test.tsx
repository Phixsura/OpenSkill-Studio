import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHelmPanel } from "@/components/fleet-helm-panel";
describe("FleetHelmPanel", () => { it("renders", () => {
    const { container } = render(<FleetHelmPanel total={20} deployed={18} failed={1} pending={1} healthy={false} />);
    expect(container.textContent).toContain("Helm Releases");
    expect(container.textContent).toContain("1 failed");
}); });
