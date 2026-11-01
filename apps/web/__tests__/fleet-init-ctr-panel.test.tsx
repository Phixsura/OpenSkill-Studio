import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetInitCtrPanel } from "@/components/fleet-init-ctr-panel";
describe("FleetInitCtrPanel", () => { it("renders", () => {
    const { container } = render(<FleetInitCtrPanel total={30} withInit={20} failedInit={2} healthy={false} />);
    expect(container.textContent).toContain("Init Containers");
    expect(container.textContent).toContain("2 init failures");
}); });
