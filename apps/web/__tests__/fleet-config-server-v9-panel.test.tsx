import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConfigServerV9Panel } from "@/components/fleet-config-server-v9-panel";
describe("FleetConfigServerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetConfigServerV9Panel configs={50} watchers={500} />);
    expect(container.textContent).toContain("Config Server v9");
}); });
