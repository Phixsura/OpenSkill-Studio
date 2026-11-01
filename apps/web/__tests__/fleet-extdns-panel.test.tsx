import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetExtdnsPanel } from "@/components/fleet-extdns-panel";
describe("FleetExtdnsPanel", () => { it("renders", () => {
    const { container } = render(<FleetExtdnsPanel total={100} synced={98} stale={2} healthy={false} />);
    expect(container.textContent).toContain("external-dns");
    expect(container.textContent).toContain("2 stale");
}); });
