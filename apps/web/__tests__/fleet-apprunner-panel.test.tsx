import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApprunnerPanel } from "@/components/fleet-apprunner-panel";
describe("FleetApprunnerPanel", () => { it("renders", () => {
    const { container } = render(<FleetApprunnerPanel services={10} running={10} instances={50} requests={5000000} />);
    expect(container.textContent).toContain("App Runner");
}); });
