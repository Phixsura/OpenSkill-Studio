import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNamespaceMgrV9Panel } from "@/components/fleet-namespace-mgr-v9-panel";
describe("FleetNamespaceMgrV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetNamespaceMgrV9Panel namespaces={30} pods={500} />);
    expect(container.textContent).toContain("Namespace Manager v9");
}); });
