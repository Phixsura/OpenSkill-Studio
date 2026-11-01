import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OnCallRotationPanel } from "@/components/oncall-rotation-panel";

describe("OnCallRotationPanel", () => {
  it("renders", () => {
    const { container } = render(
      <OnCallRotationPanel rotations={[
        { team: "platform", primary: "alice", secondary: "bob", rotationDay: 3 },
        { team: "infra", primary: "carol", secondary: "dave", rotationDay: 1 },
      ]} />
    );
    expect(container.textContent).toContain("On-Call Rotation");
    expect(container.textContent).toContain("2 teams");
    expect(container.textContent).toContain("platform");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("day 3");
  });
});
