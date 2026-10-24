import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCockroachdbPanel } from "@/components/fleet-cockroachdb-panel";
describe("FleetCockroachdbPanel", () => { it("renders", () => {
    const { container } = render(<FleetCockroachdbPanel nodes={9} live={9} ranges={30000} underReplicated={0} />);
    expect(container.textContent).toContain("CockroachDB");
    expect(container.textContent).toContain("30,000 ranges");
}); });
