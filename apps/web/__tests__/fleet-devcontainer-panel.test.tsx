import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDevcontainerPanel } from "@/components/fleet-devcontainer-panel";
describe("FleetDevcontainerPanel", () => { it("renders", () => {
    const { container } = render(<FleetDevcontainerPanel total={20} running={18} failed={2} avgStartup={35} fast={true} />);
    expect(container.textContent).toContain("DevContainers");
    expect(container.textContent).toContain("Fast startup");
}); });
