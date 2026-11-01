import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstallationHealthSummary } from "@/components/installation-health-summary";

describe("InstallationHealthSummary", () => {
  it("shows overall status", () => {
    const { container } = render(<InstallationHealthSummary total={10} healthy={8} degraded={1} critical={1} overall="healthy" />);
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("💚");
  });

  it("shows counts", () => {
    const { container } = render(<InstallationHealthSummary total={5} healthy={3} degraded={1} critical={1} overall="critical" />);
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("1");
  });

  it("shows total", () => {
    const { container } = render(<InstallationHealthSummary total={42} healthy={40} degraded={2} critical={0} overall="healthy" />);
    expect(container.textContent).toContain("42 installations");
  });
});
