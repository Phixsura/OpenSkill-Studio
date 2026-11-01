import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-key-rotation-card";

describe("ApiKeyRotationCard", () => {
  it("shows versions", () => {
    const versions = [{ version: 1, is_current: false, revoked: false, grace_remaining_min: 30 }, { version: 2, is_current: true, revoked: false, grace_remaining_min: 0 }];
    const { container } = render(<Card consumerId="c1" versions={versions} currentVersion={2} appName="App" />);
    expect(container.textContent).toContain("Key Rotation");
    expect(container.textContent).toContain("v2 active");
    expect(container.textContent).toContain("(current)");
    expect(container.textContent).toContain("30m grace");
  });
  it("shows empty", () => {
    const { container } = render(<Card consumerId="c1" versions={[]} currentVersion={0} appName="App" />);
    expect(container.textContent).toContain("No keys issued");
  });
});
