import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DnsRecordsTable } from "@/components/dns-records-table";

describe("DnsRecordsTable", () => {
  const records = [
    { type: "A", name: "@", value: "1.2.3.4", ttl: 3600 },
    { type: "CNAME", name: "www", value: "example.com", ttl: 3600 },
  ];
  it("renders records", () => {
    const { container } = render(<DnsRecordsTable records={records} onDelete={vi.fn()} />);
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("1.2.3.4");
    expect(container.textContent).toContain("CNAME");
    expect(container.textContent).toContain("DNS Records (2)");
  });
  it("delete click", () => {
    const fn = vi.fn();
    const { container } = render(<DnsRecordsTable records={records} onDelete={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
