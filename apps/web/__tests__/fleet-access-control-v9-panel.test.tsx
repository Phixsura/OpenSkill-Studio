import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAccessControlV9Panel } from "@/components/fleet-access-control-v9-panel";
describe("FleetAccessControlV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAccessControlV9Panel policies={50} roles={10} />);
    expect(container.textContent).toContain("Access Control v9");
}); });
