import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKvPanel } from "@/components/fleet-kv-panel";
describe("FleetKvPanel", () => { it("renders", () => {
    const { container } = render(<FleetKvPanel namespaces={10} keys={5000000} reads={200000000} writes={5000000} />);
    expect(container.textContent).toContain("KV Store");
}); });
