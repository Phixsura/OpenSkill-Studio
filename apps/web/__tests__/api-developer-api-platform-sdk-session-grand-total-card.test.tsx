import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKSessionGrandTotalCard from "../src/components/api-developer-api-platform-sdk-session-grand-total-card";

const total = { session_commits: 164, session_pairs: 544, session_security_fixes: 6, all_time_commits: 764, all_time_backend: 544, all_time_frontend: 544, total_components: 1088 };

describe("Card", () => {
  it("shows grand total", () => {
    const { container } = render(<APIDeveloperPlatformSDKSessionGrandTotalCard total={total} appName="OpenSkill Studio" />);
    expect(container.textContent).toContain("Session Grand Total");
    expect(container.textContent).toContain("164");
    expect(container.textContent).toContain("544");
    expect(container.textContent).toContain("764");
    expect(container.textContent).toContain("1088");
  });
});
