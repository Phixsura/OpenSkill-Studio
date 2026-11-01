import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionUpdateChecker } from "@/components/version-update-checker";

describe("VersionUpdateChecker", () => {
  it("renders versions", () => {
    const { container } = render(
      <VersionUpdateChecker updatesAvailable={2} allCurrent={false} components={[
        { name: "Next.js", current: "15.0.0", latest: "15.1.0", upToDate: false, updateType: "minor" },
        { name: "React", current: "18.3.1", latest: "18.3.1", upToDate: true, updateType: null },
        { name: "FastAPI", current: "0.115.0", latest: "1.0.0", upToDate: false, updateType: "major" },
      ]} />
    );
    expect(container.textContent).toContain("Dependencies");
    expect(container.textContent).toContain("2 updates");
    expect(container.textContent).toContain("Next.js");
    expect(container.textContent).toContain("15.1.0");
    expect(container.textContent).toContain("minor");
    expect(container.textContent).toContain("major");
    expect(container.textContent).toContain("React");
  });
});
