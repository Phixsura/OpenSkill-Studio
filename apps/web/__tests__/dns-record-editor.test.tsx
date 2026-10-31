import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DnsRecordEditor } from "@/components/dns-record-editor";

describe("DnsRecordEditor", () => {
  it("renders records", () => {
    const { container } = render(
      <DnsRecordEditor onAdd={vi.fn()} onDelete={vi.fn()} records={[
        { domain: "app.example.com", type: "A", value: "1.2.3.4", ttl: 3600 },
        { domain: "app.example.com", type: "CNAME", value: "proxy.example.com", ttl: 300 },
      ]} />
    );
    expect(container.textContent).toContain("DNS Records");
    expect(container.textContent).toContain("2 records");
    expect(container.textContent).toContain("app.example.com");
    expect(container.textContent).toContain("1.2.3.4");
    expect(container.textContent).toContain("CNAME");
  });
});
