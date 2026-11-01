import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-key-rotation-schedule-card";

describe("ConsumerApiKeyRotationScheduleCard", () => {
  it("shows schedules", () => {
    const schedules = [{ keyId: "k1", intervalDays: 90, daysUntil: 5, due: false, notify: true, autoRotate: true }, { keyId: "k2", intervalDays: 30, daysUntil: 0, due: true, notify: true, autoRotate: false }];
    const { container } = render(<Card schedules={schedules} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Key Rotation Schedule");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("auto");
    expect(container.textContent).toContain("DUE NOW");
  });
  it("shows empty", () => {
    const { container } = render(<Card schedules={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No rotation schedules");
  });
});
