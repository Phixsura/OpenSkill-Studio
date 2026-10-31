import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-sdk-download-tracker-card";

describe("SdkDownloadTrackerCard", () => {
  it("shows downloads", () => {
    const { container } = render(<Card totalDownloads={5000} byLanguage={{ typescript: 3000, python: 1500, go: 500 }} mostPopular="typescript" latestVersion="2.1.0" appName="App" />);
    expect(container.textContent).toContain("SDK Downloads");
    expect(container.textContent).toContain("typescript");
    expect(container.textContent).toContain("⭐");
    expect(container.textContent).toContain("2.1.0");
  });
  it("shows empty", () => {
    const { container } = render(<Card totalDownloads={0} byLanguage={{}} mostPopular="" latestVersion="" appName="App" />);
    expect(container.textContent).toContain("No downloads yet");
  });
});
