import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppStatusBadge } from "@/components/app-status-badge";

const STATUSES = ["draft", "testing", "submitted", "approved", "published", "deprecated", "revoked"];

describe("AppStatusBadge", () => {
  it.each(STATUSES)("renders %s status", (status) => {
    const { container } = render(<AppStatusBadge status={status} />);
    expect(container.querySelector("span")).toBeTruthy();
  });

  it.each(STATUSES.map(s => s.toUpperCase()))("renders uppercase %s", (status) => {
    const { container } = render(<AppStatusBadge status={status} />);
    expect(container.querySelector("span")).toBeTruthy();
  });

  it("renders unknown status with fallback", () => {
    const { container } = render(<AppStatusBadge status="unknown_state" />);
    expect(container.textContent).toContain("unknown_state");
  });

  it("supports md size", () => {
    const { container } = render(<AppStatusBadge status="draft" size="md" />);
    const span = container.querySelector("span");
    expect(span?.className).toContain("text-sm");
  });

  it("defaults to sm size", () => {
    const { container } = render(<AppStatusBadge status="draft" />);
    const span = container.querySelector("span");
    expect(span?.className).toContain("text-xs");
  });
});
