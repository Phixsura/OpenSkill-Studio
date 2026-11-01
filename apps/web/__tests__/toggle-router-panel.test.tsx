import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ToggleRouterPanel } from "@/components/toggle-router-panel";

describe("ToggleRouterPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ToggleRouterPanel userId="user-123" enabledCount={2} totalFlags={3}
        flags={{ dark_mode: true, new_ui: true, beta: false }} />
    );
    expect(container.textContent).toContain("Feature Toggles");
    expect(container.textContent).toContain("2/3 on");
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("ON");
    expect(container.textContent).toContain("beta");
    expect(container.textContent).toContain("OFF");
  });
});
