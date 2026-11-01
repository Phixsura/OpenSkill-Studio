import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DnsRecordTable } from "@/components/dns-record-table";

describe("DnsRecordTable", () => {
  const records = [
    { type: "A", name: "@", value: "1.2.3.4", ttl: 300 },
    { type: "CNAME", name: "www", value: "apps.openskill.dev", ttl: 3600 },
  ];
  it("renders", () => {
    const { container } = render(
      <DnsRecordTable domain="example.com" records={records} onDelete={vi.fn()} onAdd={vi.fn()} />
    );
    expect(container.textContent).toContain("DNS Records");
    expect(container.textContent).toContain("example.com");
    expect(container.textContent).toContain("1.2.3.4");
    expect(container.textContent).toContain("CNAME");
  });
  it("delete", () => {
    const fn = vi.fn();
    const { container } = render(
      <DnsRecordTable domain="x.com" records={records} onDelete={fn} onAdd={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Delete")!);
    expect(fn).toHaveBeenCalledWith("@", "A");
  });
});
