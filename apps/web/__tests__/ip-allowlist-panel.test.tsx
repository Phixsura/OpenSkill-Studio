import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IpAllowlistPanel } from "@/components/ip-allowlist-panel";

describe("IpAllowlistPanel", () => {
  it("renders rules", () => {
    const { container } = render(
      <IpAllowlistPanel rules={[
        { name: "office", cidr: "10.0.0.0/8", description: "Office network" },
        { name: "vpn", cidr: "192.168.1.0/24", description: "VPN" },
      ]} />
    );
    expect(container.textContent).toContain("IP Allowlist");
    expect(container.textContent).toContain("2 rules");
    expect(container.textContent).toContain("office");
    expect(container.textContent).toContain("10.0.0.0/8");
    expect(container.textContent).toContain("Office network");
  });
  it("renders empty", () => {
    const { container } = render(<IpAllowlistPanel rules={[]} />);
    expect(container.textContent).toContain("all IPs denied");
  });
});
