import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CustomDomainSettings } from "@/components/custom-domain-settings";

const domains = [
  { domain: "docs.myext.com", verified: true, sslActive: true, verificationToken: "abc123" },
  { domain: "app.myext.com", verified: false, sslActive: false, verificationToken: "xyz789longtoken" },
];

describe("CustomDomainSettings", () => {
  it("renders domains", () => {
    const { container } = render(<CustomDomainSettings domains={domains} />);
    expect(container.textContent).toContain("docs.myext.com");
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("Pending");
    expect(container.textContent).toContain("SSL");
  });
  it("add domain", () => {
    const fn = vi.fn();
    const { container } = render(<CustomDomainSettings domains={[]} onAdd={fn} />);
    const input = container.querySelector("input")!;
    fireEvent.change(input, { target: { value: "new.example.com" } });
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("new.example.com");
  });
});
