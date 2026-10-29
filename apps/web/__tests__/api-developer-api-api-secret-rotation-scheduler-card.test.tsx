import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiSecretRotationSchedulerCard from "../src/components/api-developer-api-api-secret-rotation-scheduler-card";

const schedules = [
  { secret_id: "prod-key", secret_type: "api_key", days_until_rotation: 45, rotation_count: 3, overdue: false },
  { secret_id: "hook-secret", secret_type: "webhook_secret", days_until_rotation: 0, rotation_count: 1, overdue: true },
];

describe("APIDeveloperAPIApiSecretRotationSchedulerCard", () => {
  it("shows rotation schedules", () => {
    const { container } = render(<APIDeveloperAPIApiSecretRotationSchedulerCard schedules={schedules} overdueCount={1} appName="App" />);
    expect(container.textContent).toContain("Secret Rotation");
    expect(container.textContent).toContain("1 overdue");
    expect(container.textContent).toContain("prod-key");
    expect(container.textContent).toContain("45d");
    expect(container.textContent).toContain("OVERDUE");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiSecretRotationSchedulerCard schedules={[]} overdueCount={0} appName="App" />);
    expect(container.textContent).toContain("No rotation schedules");
  });
});
