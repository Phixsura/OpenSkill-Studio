import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperSDKDownloadCard from "../src/components/api-developer-sdk-download-card";

const langs = [
  { language: "JavaScript", downloads: 7000 },
  { language: "Python", downloads: 3000 },
];

describe("APIDeveloperSDKDownloadCard", () => {
  it("shows downloads", () => {
    const { container } = render(<APIDeveloperSDKDownloadCard languages={langs} totalDownloads={10000} appName="App" />);
    expect(container.textContent).toContain("SDK Downloads");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("JavaScript");
    expect(container.textContent).toContain("70%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperSDKDownloadCard languages={[]} totalDownloads={0} appName="App" />);
    expect(container.textContent).toContain("No downloads yet");
  });
});
