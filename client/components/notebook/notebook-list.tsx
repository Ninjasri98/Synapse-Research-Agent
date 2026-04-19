import { NotebookCard } from "@/components/notebook/notebook-card";
import { CreateNotebookDialog } from "@/components/notebook/create-notebook-dialog";
import { BookOpen } from "lucide-react";

type NotebookSource = {
  id: string;
  sourceType: string;
  sourceUrl?: string | null;
  content?: string | null;
};

type Notebook = {
  id: string;
  title: string | null;
  topic: string | null;
  createdAt: Date;
  updatedAt: Date;
  sources?: NotebookSource[];
  processingStatus?: {
    status: "IN_QUEUE" | "IN_PROGRESS" | "PROCESSED" | "ERROR";
    message: string | null;
  } | null;
};

type NotebookListProps = {
  notebooks: Notebook[];
};

export function NotebookList({ notebooks }: NotebookListProps) {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Your Notebooks</h1>
        <CreateNotebookDialog />
      </div>

      {notebooks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium">No notebooks yet</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Create your first notebook to get started
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {notebooks.map((notebook) => (
            <NotebookCard key={notebook.id} notebook={notebook} />
          ))}
        </div>
      )}
    </div>
  );
}
