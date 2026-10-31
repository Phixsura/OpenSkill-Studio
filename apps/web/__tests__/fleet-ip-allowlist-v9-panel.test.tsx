import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIpAllowlistV9Panel } from "@/components/fleet-ip-allowlist-v9-panel";
describe("FleetIpAllowlistV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetIpAllowlistV9Panel rules={20} blocked={500} />);
    expect(container.textContent).toContain("IP Allowlist v9");
}); });
