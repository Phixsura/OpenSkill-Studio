import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVercelPanel } from "@/components/fleet-vercel-panel";
describe("FleetVercelPanel", () => { it("renders", () => {
    const { container } = render(<FleetVercelPanel projects={15} deployed={15} requests={20000000} edgeFunctions={30} />);
    expect(container.textContent).toContain("Vercel");
    expect(container.textContent).toContain("30 edge fn");
}); });
