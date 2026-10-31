import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-sdk-download-tracker-card";

describe("SdkDownloadTrackerCard", () => {
  it("shows downloads", () => {
    const versions = [{ version: "2.0", downloads: 5000 }];
    const languages = [{ language: "python", downloads: 3000 }, { language: "typescript", downloads: 2000 }];
    const { container } = render(<Card sdkName="my-sdk" totalDownloads={5000} languages={languages} versions={versions} appName="App" />);
    expect(container.textContent).toContain("SDK Downloads");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("python: 3,000");
  });
  it("shows empty versions", () => {
    const { container } = render(<Card sdkName="sdk" totalDownloads={0} languages={[]} versions={[]} appName="App" />);
    expect(container.textContent).toContain("SDK Downloads");
  });
});
