import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppInstallCount } from "@/components/app-install-count";

describe("AppInstallCount", () => {
  it("shows count", () => {
    const { container } = render(<AppInstallCount count={42} />);
    expect(container.textContent).toContain("42");
  });

  it("formats thousands", () => {
    const { container } = render(<AppInstallCount count={5000} />);
    expect(container.textContent).toContain("5.0k");
  });

  it("shows trend up", () => {
    const { container } = render(<AppInstallCount count={100} trend="up" />);
    expect(container.textContent).toContain("📈");
  });

  it("pluralizes", () => {
    const { container } = render(<AppInstallCount count={1} />);
    expect(container.textContent).toContain("install ");
  });
});
