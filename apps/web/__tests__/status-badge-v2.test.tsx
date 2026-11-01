import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadgeV2 } from "@/components/status-badge-v2";

describe("StatusBadgeV2", () => {
  it("published", () => {
    const { container } = render(<StatusBadgeV2 status="published" />);
    expect(container.textContent).toContain("Published");
    expect(container.querySelector("[class*='bg-green']")).toBeTruthy();
  });
  it("draft", () => {
    const { container } = render(<StatusBadgeV2 status="draft" />);
    expect(container.textContent).toContain("Draft");
  });
  it("suspended", () => {
    const { container } = render(<StatusBadgeV2 status="suspended" />);
    expect(container.textContent).toContain("Suspended");
    expect(container.querySelector("[class*='bg-red']")).toBeTruthy();
  });
  it("unknown defaults to draft", () => {
    const { container } = render(<StatusBadgeV2 status="unknown_status" />);
    expect(container.textContent).toContain("Draft");
  });
});
