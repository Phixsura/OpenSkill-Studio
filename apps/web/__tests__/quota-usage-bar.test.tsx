import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuotaUsageBar } from "@/components/quota-usage-bar";

describe("QuotaUsageBar", () => {
  it("renders resource name", () => {
    const { container } = render(<QuotaUsageBar resource="apps" current={3} limit={10} />);
    expect(container.textContent).toContain("apps");
  });

  it("shows usage count", () => {
    const { container } = render(<QuotaUsageBar resource="apps" current={3} limit={10} />);
    expect(container.textContent).toContain("3 / 10");
  });

  it("shows warning at 90%", () => {
    const { container } = render(<QuotaUsageBar resource="apps" current={9} limit={10} />);
    expect(container.textContent).toContain("Approaching limit");
  });

  it("no warning at low usage", () => {
    const { container } = render(<QuotaUsageBar resource="apps" current={1} limit={10} />);
    expect(container.textContent).not.toContain("Approaching");
  });

  it("formats resource name", () => {
    const { container } = render(<QuotaUsageBar resource="api_keys" current={2} limit={5} />);
    expect(container.textContent).toContain("api keys");
  });
});
