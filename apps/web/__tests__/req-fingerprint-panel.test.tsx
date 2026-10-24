import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqFingerprintPanel } from "@/components/req-fingerprint-panel";
describe("ReqFingerprintPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqFingerprintPanel uniqueFingerprints={500} duplicateGroups={50}
        totalRequests={1000} dedupSavingsPct={50} />
    );
    expect(container.textContent).toContain("Request Fingerprints");
    expect(container.textContent).toContain("500 unique / 1000 total");
    expect(container.textContent).toContain("50% dedup");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("50");
  });
});
