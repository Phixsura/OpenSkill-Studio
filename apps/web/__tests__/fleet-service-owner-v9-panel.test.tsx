import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceOwnerV9Panel } from "@/components/fleet-service-owner-v9-panel";
describe("FleetServiceOwnerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceOwnerV9Panel services={200} withOwner={200} />);
    expect(container.textContent).toContain("Service Owner v9");
}); });
