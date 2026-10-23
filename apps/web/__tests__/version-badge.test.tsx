import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionBadge } from "@/components/version-badge";

describe("VersionBadge", () => {
  it("renders stable", () => {
    const { container } = render(
      <VersionBadge display="v2.1.0" channelInfo={{ color: "green", icon: "✅", label: "Stable" }} isLatest={true} />
    );
    expect(container.textContent).toContain("✅ v2.1.0");
    expect(container.textContent).toContain("Latest");
  });
  it("renders beta", () => {
    const { container } = render(
      <VersionBadge display="v3.0.0-beta" channelInfo={{ color: "yellow", icon: "🧪", label: "Beta" }} isLatest={false} />
    );
    expect(container.textContent).toContain("🧪 v3.0.0-beta");
    expect(container.textContent).not.toContain("Latest");
  });
});
