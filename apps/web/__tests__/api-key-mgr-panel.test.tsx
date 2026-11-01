import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiKeyMgrPanel } from "@/components/api-key-mgr-panel";

describe("ApiKeyMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ApiKeyMgrPanel toRotate={1} active={2}
        keys={[
          { preview: "osk_abc1...xyz1", ageDays: 100, needsRotation: true },
          { preview: "osk_def2...xyz2", ageDays: 10, needsRotation: false },
        ]} />
    );
    expect(container.textContent).toContain("API Keys");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("1 need rotation");
    expect(container.textContent).toContain("osk_abc1...xyz1");
    expect(container.textContent).toContain("ROTATE");
    expect(container.textContent).toContain("10d old");
  });
});
