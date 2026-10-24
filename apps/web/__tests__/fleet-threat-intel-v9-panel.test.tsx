import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetThreatIntelV9Panel } from "@/components/fleet-threat-intel-v9-panel";
describe("FleetThreatIntelV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetThreatIntelV9Panel feeds={10} blocked={50} />);
    expect(container.textContent).toContain("Threat Intel v9");
}); });
