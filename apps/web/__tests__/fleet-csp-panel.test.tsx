import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCspPanel } from "@/components/fleet-csp-panel";
describe("FleetCspPanel", () => { it("renders", () => {
    const { container } = render(<FleetCspPanel total={10} withCsp={8} strict={5} coveragePct={80} />);
    expect(container.textContent).toContain("CSP Coverage");
    expect(container.textContent).toContain("80% with CSP");
}); });
