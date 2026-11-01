import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DomainSetup } from "@/components/domain-setup";

describe("DomainSetup", () => {
  it("renders input and verify button", () => {
    const { container } = render(<DomainSetup onVerify={vi.fn()} record={null} verified={false} />);
    expect(container.textContent).toContain("Custom Domain");
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.textContent).toContain("Verify");
  });
  it("shows DNS record", () => {
    const record = { type: "TXT", name: "_openskill-verify.example.com", value: "openskill-verify=abc123" };
    const { container } = render(<DomainSetup onVerify={vi.fn()} record={record} verified={false} />);
    expect(container.textContent).toContain("TXT");
    expect(container.textContent).toContain("_openskill-verify");
  });
  it("shows verified state", () => {
    const { container } = render(<DomainSetup onVerify={vi.fn()} record={null} verified={true} />);
    expect(container.textContent).toContain("Domain verified!");
  });
});
