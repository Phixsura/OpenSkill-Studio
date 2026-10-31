import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiChangelogV9Panel } from "@/components/fleet-api-changelog-v9-panel";
describe("FleetApiChangelogV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiChangelogV9Panel apis={20} entries={500} />);
    expect(container.textContent).toContain("API Changelog v9");
}); });
