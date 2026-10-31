import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-consumer-api-api-consumer-api-consumer-api-settings-card";

describe("ConsumerApiSettingsCard", () => {
  it("shows settings", () => {
    const settings = [{ key: "theme", value: "dark", category: "display", isSecret: false }, { key: "api_secret", value: "***", category: "security", isSecret: true }];
    const { container } = render(<Card settings={settings} categories={["display", "security"]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Consumer Settings");
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("dark");
    expect(container.textContent).toContain("***");
  });
  it("shows empty", () => {
    const { container } = render(<Card settings={[]} categories={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No settings");
  });
});
