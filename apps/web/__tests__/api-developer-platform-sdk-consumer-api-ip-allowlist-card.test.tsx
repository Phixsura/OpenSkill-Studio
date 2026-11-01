import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IpAllowlistCard from "../src/components/api-developer-platform-sdk-consumer-api-ip-allowlist-card";

describe("IpAllowlistCard", () => {
  it("renders title and entries", () => {
    const { container } = render(<IpAllowlistCard />);
    expect(container.textContent).toContain("IP Allowlist");
    expect(container.textContent).toContain("10.0.0.0/24");
    expect(container.textContent).toContain("Office");
  });

  it("shows mode and entry count", () => {
    const { container } = render(<IpAllowlistCard />);
    expect(container.textContent).toContain("allow mode");
    expect(container.textContent).toContain("3 entries configured");
  });
});
