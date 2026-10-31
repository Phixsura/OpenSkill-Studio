import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPrivilegeMgrV9Panel } from "@/components/fleet-privilege-mgr-v9-panel";
describe("FleetPrivilegeMgrV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPrivilegeMgrV9Panel total={100} approved={90} />);
    expect(container.textContent).toContain("Privilege Manager v9");
}); });
