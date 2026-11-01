import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiVersionSwitcher } from "@/components/api-version-switcher";

describe("ApiVersionSwitcher", () => {
  it("renders and switches", () => {
    const onSwitch = vi.fn();
    const { container, getByText } = render(
      <ApiVersionSwitcher current="v2" onSwitch={onSwitch} versions={[
        { version: "v2", status: "stable", endpointCount: 15 },
        { version: "v1", status: "deprecated", sunsetDate: "2027-01-01", endpointCount: 10 },
      ]} />
    );
    expect(container.textContent).toContain("API Versions");
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("stable");
    expect(container.textContent).toContain("Sunset: 2027-01-01");
    fireEvent.click(getByText("v1"));
    expect(onSwitch).toHaveBeenCalledWith("v1");
  });
});
