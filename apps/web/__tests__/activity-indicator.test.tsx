import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActivityIndicator } from "@/components/activity-indicator";

describe("ActivityIndicator", () => {
  it("renders with label", () => {
    const { container } = render(
      <ActivityIndicator status="active" label="Active now" dot="🟢" />
    );
    expect(container.textContent).toContain("🟢");
    expect(container.textContent).toContain("Active now");
  });
  it("hides label", () => {
    const { container } = render(
      <ActivityIndicator status="offline" label="Offline" dot="⚫" showLabel={false} />
    );
    expect(container.textContent).toContain("⚫");
    expect(container.textContent).not.toContain("Offline");
  });
});
