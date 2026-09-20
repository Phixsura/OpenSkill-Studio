"use client";

export default function AuthError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-xl font-bold">Authentication Error</h1>
        <p className="mt-2 text-gray-600">{error.message || "Something went wrong"}</p>
        <button onClick={reset} className="mt-4 rounded bg-blue-600 px-4 py-2 text-white">
          Try again
        </button>
      </div>
    </div>
  );
}
