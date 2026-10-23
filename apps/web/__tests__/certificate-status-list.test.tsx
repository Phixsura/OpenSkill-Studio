import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CertificateStatusList } from "@/components/certificate-status-list";

describe("CertificateStatusList", () => {
  const certs = [
    { domain: "a.com", days_until_expiry: 60, status: "valid", auto_renew: true },
    { domain: "b.com", days_until_expiry: 5, status: "expiring", auto_renew: false },
  ];
  it("renders", () => {
    const { container } = render(<CertificateStatusList certificates={certs} onRenew={vi.fn()} />);
    expect(container.textContent).toContain("SSL Certificates");
    expect(container.textContent).toContain("a.com");
    expect(container.textContent).toContain("60 days left");
    expect(container.textContent).toContain("Auto-renew");
    expect(container.textContent).toContain("expiring");
  });
  it("renew", () => {
    const fn = vi.fn();
    const { container } = render(<CertificateStatusList certificates={certs} onRenew={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Renew")!);
    expect(fn).toHaveBeenCalledWith("b.com");
  });
});
