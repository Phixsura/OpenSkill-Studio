import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DnsHealthPanel } from "@/components/dns-health-panel";

describe("DnsHealthPanel", () => {
  it("renders DNS checks", () => {
    const { container } = render(
      <DnsHealthPanel domain="app.example.com" allOk={false} propagationPct={67}
        checks={[
          { type: "A", name: "app.example.com", expected: "1.2.3.4", resolved: true },
          { type: "TXT", name: "app.example.com", expected: "", resolved: false },
        ]} />
    );
    expect(container.textContent).toContain("DNS: app.example.com");
    expect(container.textContent).toContain("Issues");
    expect(container.textContent).toContain("67% propagated");
    expect(container.textContent).toContain("1.2.3.4");
  });
});
