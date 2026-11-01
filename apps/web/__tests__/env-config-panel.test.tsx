import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvConfigPanel } from "@/components/env-config-panel";

const configs = {
  development: { API_URL: "http://localhost", DEBUG: "true" },
  staging: { API_URL: "https://staging.app.com" },
  production: {},
};

describe("EnvConfigPanel", () => {
  it("renders config values", () => {
    const { container } = render(<EnvConfigPanel configs={configs} activeEnv="development" />);
    expect(container.textContent).toContain("API_URL");
    expect(container.textContent).toContain("http://localhost");
    expect(container.textContent).toContain("Promote to staging");
  });
  it("switch env", () => {
    const fn = vi.fn();
    const { container } = render(<EnvConfigPanel configs={configs} activeEnv="development" onSwitch={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]); // staging
    expect(fn).toHaveBeenCalledWith("staging");
  });
});
