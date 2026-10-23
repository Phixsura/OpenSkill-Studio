import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DnsRecordEditor } from "@/components/dns-record-editor";

describe("DnsRecordEditor", () => {
  it("renders records", () => {
    const onRemove = vi.fn();
    const { container, getAllByText } = render(
      <DnsRecordEditor domain="example.com" onAdd={vi.fn()} onRemove={onRemove}
        records={[
          { type: "A", name: "@", value: "93.184.216.34", ttl: 3600 },
          { type: "CNAME", name: "www", value: "example.com", ttl: 3600 },
        ]} />
    );
    expect(container.textContent).toContain("DNS Records");
    expect(container.textContent).toContain("example.com");
    expect(container.textContent).toContain("93.184.216.34");
    expect(container.textContent).toContain("CNAME");
    fireEvent.click(getAllByText("Delete")[0]);
    expect(onRemove).toHaveBeenCalledWith("@", "A");
  });
});
