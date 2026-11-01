import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetScylladbPanel } from "@/components/fleet-scylladb-panel";
describe("FleetScylladbPanel", () => { it("renders", () => {
    const { container } = render(<FleetScylladbPanel nodes={6} up={6} opsPerSec={600000} p99={2} />);
    expect(container.textContent).toContain("ScyllaDB");
    expect(container.textContent).toContain("600,000 ops/s");
}); });
