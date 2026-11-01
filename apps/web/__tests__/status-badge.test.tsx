import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadge } from "@/components/status-badge";

describe("StatusBadge", () => {
  it("renders active status", () => {
    const { container } = render(<StatusBadge status="active" />);
    expect(container.querySelector("span")).toBeTruthy();
  });

  it("renders suspended status", () => {
    const { container } = render(<StatusBadge status="suspended" />);
    expect(container.querySelector("span")).toBeTruthy();
  });

  it("renders unknown status gracefully", () => {
    const { container } = render(<StatusBadge status="something_new" />);
    expect(container.querySelector("span")).toBeTruthy();
  });
});
