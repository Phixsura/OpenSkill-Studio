import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MaintenanceModeCard from "../src/components/api-developer-platform-sdk-consumer-api-maintenance-mode-card";

describe("MaintenanceModeCard", () => {
  it("renders title and status", () => {
    const { container } = render(<MaintenanceModeCard />);
    expect(container.textContent).toContain("Maintenance Mode");
    expect(container.textContent).toContain("OFF");
    expect(container.textContent).toContain("All systems operational");
  });

  it("shows bypass and IP counts", () => {
    const { container } = render(<MaintenanceModeCard />);
    expect(container.textContent).toContain("2 bypass keys");
    expect(container.textContent).toContain("3 allowed IPs");
  });
});
