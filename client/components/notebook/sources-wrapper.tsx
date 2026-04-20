"use client";

import { Suspense } from "react";
import dynamic from "next/dynamic";
import { NotebookSource } from "@/components/notebook/edit-notebook-sources";

// Dynamic import in a client component is allowed with ssr: false
const EditNotebookSources = dynamic(
  () => import("@/components/notebook/edit-notebook-sources"),
  { ssr: false }
);

type SourcesWrapperProps = {
  // notebookId: string;
  initialSources: NotebookSource[];
  // disabled?: boolean;
};

export function SourcesWrapper({
  // notebookId,
  initialSources,
  // disabled,
}: SourcesWrapperProps) {
  return (
    <Suspense
      fallback={<div className="p-4 text-center">Loading sources...</div>}
    >
      <EditNotebookSources
        // notebookId={notebookId}
        initialSources={initialSources}
        // disabled={disabled}
      />
    </Suspense>
  );
}
