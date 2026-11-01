import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSecurityEventV9Panel } from "@/components/fleet-security-event-v9-panel";
describe("FleetSecurityEventV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSecurityEventV9Panel total={500} critical={0} />);
    expect(container.textContent).toContain("Security Event v9");
}); });
