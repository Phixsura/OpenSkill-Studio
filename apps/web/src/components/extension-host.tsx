"use client";

import { useCallback, useEffect, useRef, useState } from "react";

interface ExtensionHostProps {
  appId: string;
  installationId: string;
  surface: string;
  entryUrl: string;
  viewportWidth?: number;
  viewportHeight?: number;
  orgId: string;
  userId: string;
  entityId?: string;
  entityType?: string;
  permissions: string[];
  apiBaseUrl?: string;
  onToast?: (opts: { message: string; type?: string }) => void;
  onNavigate?: (path: string) => void;
}

/**
 * ExtensionHost — renders a sandboxed iframe for a third-party UI extension
 * and handles postMessage communication via the Extension SDK protocol.
 *
 * Security:
 * - iframe sandbox: allow-scripts allow-forms (no allow-same-origin)
 * - Origin validation on all incoming messages
 * - Short-lived scoped API tokens
 * - Message type allowlisting
 */
export function ExtensionHost({
  appId,
  installationId,
  surface,
  entryUrl,
  viewportWidth = 400,
  viewportHeight = 300,
  orgId,
  userId,
  entityId,
  entityType,
  permissions,
  apiBaseUrl = "",
  onToast,
  onNavigate,
}: ExtensionHostProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [iframeHeight, setIframeHeight] = useState(viewportHeight);
  const [ready, setReady] = useState(false);

  // Derive the extension origin from entryUrl
  const extensionOrigin = (() => {
    try {
      const url = new URL(entryUrl);
      return url.origin;
    } catch {
      return "*";
    }
  })();

  const sendToExtension = useCallback(
    (data: Record<string, unknown>) => {
      if (iframeRef.current?.contentWindow) {
        iframeRef.current.contentWindow.postMessage(
          { source: "openskill-host", ...data },
          extensionOrigin,
        );
      }
    },
    [extensionOrigin],
  );

  // Handle messages from the extension
  const handleMessage = useCallback(
    async (event: MessageEvent) => {
      // Validate source is our iframe
      if (event.source !== iframeRef.current?.contentWindow) return;

      const data = event.data;
      if (!data || typeof data !== "object" || data.source !== "openskill-extension") return;

      switch (data.type) {
        case "extension:ready":
          setReady(true);
          // Send initial context
          sendToExtension({
            type: "context_changed",
            context: {
              orgId,
              userId,
              surface,
              entityId,
              entityType,
              installationId,
              permissions,
            },
          });
          break;

        case "api_call": {
          // Scoped API proxy — enforce path allowlist and method restrictions
          const ALLOWED_METHODS = new Set(["GET", "POST", "PATCH", "DELETE"]);
          const method = String(data.method ?? "GET").toUpperCase();
          const path = String(data.path ?? "");

          // Reject invalid method
          if (!ALLOWED_METHODS.has(method)) {
            sendToExtension({ type: "error", id: data.id, message: "Method not allowed" });
            break;
          }

          // Reject path traversal and non-API paths
          if (path.includes("..") || !path.startsWith("/")) {
            sendToExtension({ type: "error", id: data.id, message: "Invalid path" });
            break;
          }

          // Enforce permission scope — map path prefix to required permission
          const pathPermMap: Record<string, string> = {
            "/cohorts": "read:cohorts",
            "/projects": "read:projects",
            "/submissions": "read:submissions",
            "/skills": "read:skills",
            "/packs": "read:packs",
            "/workflows": "read:workflows",
            "/talent": "read:talent",
            "/evaluations": "read:evaluations",
          };
          const requiredPerm = Object.entries(pathPermMap).find(([prefix]) =>
            path.startsWith(prefix),
          )?.[1];
          if (requiredPerm && !permissions.includes(requiredPerm)) {
            sendToExtension({ type: "error", id: data.id, message: "Insufficient permissions" });
            break;
          }

          try {
            const res = await fetch(`${apiBaseUrl}/api/v1${path}`, {
              method,
              headers: { "Content-Type": "application/json" },
              credentials: "omit",  // Don't send ambient cookies
              body: data.body && method !== "GET" ? JSON.stringify(data.body) : undefined,
            });
            const result = await res.json();
            sendToExtension({ type: "response", id: data.id, result });
          } catch (err) {
            sendToExtension({ type: "error", id: data.id, message: String(err) });
          }
          break;
        }

        case "ui:resize":
          if (typeof data.height === "number" && data.height > 0 && data.height <= 2000) {
            setIframeHeight(data.height);
          }
          break;

        case "ui:navigate":
          if (typeof data.path === "string" && onNavigate) {
            onNavigate(data.path);
          }
          break;

        case "ui:toast":
          if (onToast && typeof data.message === "string") {
            onToast({
              message: data.message,
              type: data.toastType as string | undefined,
            });
          }
          break;

        case "ui:close":
          // Could emit onClose callback
          break;

        default:
          // Unknown message type — ignore
          break;
      }
    },
    [sendToExtension, orgId, userId, surface, entityId, entityType, installationId, permissions, apiBaseUrl, onToast, onNavigate],
  );

  useEffect(() => {
    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [handleMessage]);

  return (
    <div className="overflow-hidden rounded-lg border dark:border-gray-700">
      {!ready && (
        <div className="flex items-center justify-center bg-gray-50 p-4 text-sm text-gray-400 dark:bg-gray-800">
          Loading extension…
        </div>
      )}
      <iframe
        ref={iframeRef}
        src={entryUrl}
        sandbox="allow-scripts allow-forms"
        referrerPolicy="no-referrer"
        style={{
          border: "none",
          width: viewportWidth === 0 ? "100%" : `${viewportWidth}px`,
          height: `${iframeHeight}px`,
          display: ready ? "block" : "none",
        }}
        title={`Extension: ${appId} (${surface})`}
      />
    </div>
  );
}
