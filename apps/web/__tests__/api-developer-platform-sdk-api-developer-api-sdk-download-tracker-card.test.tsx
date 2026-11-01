import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTrackerCard from "../src/components/api-developer-platform-sdk-api-developer-api-sdk-download-tracker-card";

describe("Card", () => {
  it("shows SDK downloads", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTrackerCard totalDownloads={50000} languageBreakdown={{ python: 30000, javascript: 20000 }} popularSDKs={[["openskill-sdk", 50000]]} appName="App" />);
    expect(container.textContent).toContain("SDK Downloads");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("python: 30,000");
    expect(container.textContent).toContain("openskill-sdk");
  });
});
