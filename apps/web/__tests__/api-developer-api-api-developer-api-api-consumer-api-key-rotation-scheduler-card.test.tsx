import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationSchedulerCard from "../src/components/api-developer-api-api-developer-api-api-consumer-api-key-rotation-scheduler-card";

const schedules = [
  { consumer_id: "acme", key_id: "prod-key", days_until_rotation: 45, rotation_count: 3, overdue: false, auto_rotate: true },
  { consumer_id: "beta", key_id: "test-key", days_until_rotation: 0, rotation_count: 0, overdue: true, auto_rotate: true },
];

describe("Card", () => {
  it("shows schedules", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationSchedulerCard schedules={schedules} overdueCount={1} appName="App" />);
    expect(container.textContent).toContain("Key Rotation");
    expect(container.textContent).toContain("1 overdue");
    expect(container.textContent).toContain("acme / prod-key");
    expect(container.textContent).toContain("OVERDUE");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerApiKeyRotationSchedulerCard schedules={[]} overdueCount={0} appName="App" />);
    expect(container.textContent).toContain("No rotation schedules");
  });
});
