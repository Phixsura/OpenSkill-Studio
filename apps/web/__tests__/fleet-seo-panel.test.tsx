import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSeoPanel } from "@/components/fleet-seo-panel";
describe("FleetSeoPanel", () => { it("renders", () => {
    const { container } = render(<FleetSeoPanel total={30} avgScore={85} poorPages={2} good={true} />);
    expect(container.textContent).toContain("SEO Score");
    expect(container.textContent).toContain("85/100");
}); });
