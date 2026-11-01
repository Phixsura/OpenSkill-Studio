import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContainerSecurityV9Panel } from "@/components/fleet-container-security-v9-panel";
describe("FleetContainerSecurityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContainerSecurityV9Panel containers={500} nonRoot={500} />);
    expect(container.textContent).toContain("Container Security v9");
}); });
