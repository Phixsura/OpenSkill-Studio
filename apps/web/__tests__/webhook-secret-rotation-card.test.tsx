import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookSecretRotationCard from "../src/components/webhook-secret-rotation-card";

const rotations = [
  { rotation_id: "r1", in_grace_period: true, completed: false },
  { rotation_id: "r2", in_grace_period: false, completed: true },
];

describe("WebhookSecretRotationCard", () => {
  it("renders header and active status", () => {
    const { container } = render(<WebhookSecretRotationCard rotations={rotations} hasSecret={true} appName="App" />);
    expect(container.textContent).toContain("Secret Rotation");
    expect(container.textContent).toContain("Active");
  });

  it("shows grace period alert", () => {
    const { container } = render(<WebhookSecretRotationCard rotations={rotations} hasSecret={true} appName="App" />);
    expect(container.textContent).toContain("1 rotation in grace period");
  });

  it("shows rotation statuses", () => {
    const { container } = render(<WebhookSecretRotationCard rotations={rotations} hasSecret={true} appName="App" />);
    expect(container.textContent).toContain("grace period");
    expect(container.textContent).toContain("completed");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookSecretRotationCard rotations={[]} hasSecret={false} appName="App" />);
    expect(container.textContent).toContain("No rotations");
    expect(container.textContent).toContain("Not set");
  });
});
