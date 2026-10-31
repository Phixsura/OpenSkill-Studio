import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-version-pinning-card";

describe("ConsumerApiVersionPinningCard", () => {
  it("shows pins", () => {
    const pins = [{ consumer_id: "c1", pinned_version: "v2.0", reason: "Compat", auto_upgrade: true }];
    const { container } = render(<Card pins={pins} appName="App" />);
    expect(container.textContent).toContain("Version Pinning");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("auto");
  });
  it("shows empty", () => {
    const { container } = render(<Card pins={[]} appName="App" />);
    expect(container.textContent).toContain("No version pins");
  });
});
