import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IPAllowlistCard from "../src/components/ip-allowlist-card";

const entries = [
  { entry_id: "e1", cidr: "10.0.0.0/24", label: "Office", is_expired: false },
  { entry_id: "e2", cidr: "192.168.1.1/32", label: "VPN", is_expired: false },
  { entry_id: "e3", cidr: "172.16.0.0/16", label: "Temp", is_expired: true },
];

describe("IPAllowlistCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<IPAllowlistCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("IP Allowlist");
    expect(container.textContent).toContain("2 active rules");
  });

  it("shows CIDR ranges", () => {
    const { container } = render(<IPAllowlistCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("10.0.0.0/24");
    expect(container.textContent).toContain("192.168.1.1/32");
  });

  it("shows labels", () => {
    const { container } = render(<IPAllowlistCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("Office");
    expect(container.textContent).toContain("VPN");
  });

  it("shows expired badge", () => {
    const { container } = render(<IPAllowlistCard entries={entries} appName="App" />);
    expect(container.textContent).toContain("expired");
  });

  it("shows empty deny-all state", () => {
    const { container } = render(<IPAllowlistCard entries={[]} appName="App" />);
    expect(container.textContent).toContain("No IP rules");
  });
});
