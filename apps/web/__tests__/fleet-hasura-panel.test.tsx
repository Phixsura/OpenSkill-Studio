import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHasuraPanel } from "@/components/fleet-hasura-panel";
describe("FleetHasuraPanel", () => { it("renders", () => {
    const { container } = render(<FleetHasuraPanel instances={5} healthy={5} tables={200} requests={20000000} />);
    expect(container.textContent).toContain("Hasura");
    expect(container.textContent).toContain("20,000,000");
}); });
