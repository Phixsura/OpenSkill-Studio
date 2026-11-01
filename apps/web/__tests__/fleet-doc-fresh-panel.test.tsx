import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDocFreshPanel } from "@/components/fleet-doc-fresh-panel";
describe("FleetDocFreshPanel", () => { it("renders", () => {
    const { container } = render(<FleetDocFreshPanel total={50} fresh={40} stale={10} freshnessPct={80} />);
    expect(container.textContent).toContain("Doc Freshness");
    expect(container.textContent).toContain("10 stale");
}); });
