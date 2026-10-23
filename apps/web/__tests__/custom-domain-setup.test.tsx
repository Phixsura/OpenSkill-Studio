import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CustomDomainSetup } from "@/components/custom-domain-setup";

describe("CustomDomainSetup", () => {
  const dns = [
    { type: "CNAME", name: "myapp.example.com", value: "apps.openskill.dev" },
    { type: "TXT", name: "_verify.myapp.example.com", value: "openskill-verify=a1" },
  ];
  it("renders", () => {
    const { container } = render(
      <CustomDomainSetup domain="myapp.example.com" dnsRecords={dns} sslStatus="pending"
        verificationStatus="pending" onVerify={vi.fn()} />
    );
    expect(container.textContent).toContain("Custom Domain");
    expect(container.textContent).toContain("myapp.example.com");
    expect(container.textContent).toContain("CNAME");
    expect(container.textContent).toContain("SSL: pending");
  });
  it("verify", () => {
    const fn = vi.fn();
    const { container } = render(
      <CustomDomainSetup domain="x.com" dnsRecords={dns} sslStatus="pending"
        verificationStatus="pending" onVerify={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Verify DNS")!);
    expect(fn).toHaveBeenCalled();
  });
});
