import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionSunsetPanel } from "@/components/version-sunset-panel";
describe("VersionSunsetPanel", () => {
  it("renders", () => {
    const { container } = render(
      <VersionSunsetPanel active={1} sunsetting={1} sunset={1}
        versions={[
          { version: "v3", status: "active" },
          { version: "v2", status: "sunsetting", daysLeft: 60 },
          { version: "v1", status: "sunset" },
        ]} />
    );
    expect(container.textContent).toContain("Version Sunsets");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("1 sunsetting");
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("60d");
  });
});
