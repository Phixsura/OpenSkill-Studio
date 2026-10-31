import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPerfProfileV9Panel } from "@/components/fleet-perf-profile-v9-panel";
describe("FleetPerfProfileV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPerfProfileV9Panel profiles={20} hotspots={5} />);
    expect(container.textContent).toContain("Perf Profile v9");
}); });
