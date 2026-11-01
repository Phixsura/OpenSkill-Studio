import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAppConfigCard from "../src/components/api-developer-app-config-card";

const apps = [{ app_id: "app-1", name: "My App", setting_count: 5, flag_count: 3 }];

describe("APIDeveloperAppConfigCard", () => {
  it("shows apps", () => {
    const { container } = render(<APIDeveloperAppConfigCard apps={apps} appName="Platform" />);
    expect(container.textContent).toContain("App Configs");
    expect(container.textContent).toContain("My App");
    expect(container.textContent).toContain("5 settings");
    expect(container.textContent).toContain("3 flags");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAppConfigCard apps={[]} appName="Platform" />);
    expect(container.textContent).toContain("No app configs");
  });
});
