import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChangelogPanel } from "@/components/fleet-changelog-panel";
describe("FleetChangelogPanel", () => { it("renders", () => {
    const { container } = render(<FleetChangelogPanel total={50} features={30} fixes={18} breaking={2} />);
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("30 features");
}); });
