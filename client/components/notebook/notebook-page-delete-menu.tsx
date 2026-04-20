"use client";

import { DeleteNotebookMenu } from "@/components/notebook/delete-notebook-menu";

interface NotebookPageDeleteMenuProps {
  notebookId: string;
  className?: string;
  disabled?: boolean;
}

export function NotebookPageDeleteMenu({
  notebookId,
  className,
  disabled,
}: NotebookPageDeleteMenuProps) {
  return (
    <DeleteNotebookMenu
      notebookId={notebookId}
      className={className}
      disabled={disabled}
    />
  );
}
