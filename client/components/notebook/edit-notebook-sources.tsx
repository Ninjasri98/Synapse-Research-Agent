"use client";

import { useState } from "react";
import { X, Link as LinkIcon, FileText, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { FileUpload } from "@/components/ui/file-upload";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Match the Prisma enum
export type NotebookDocumentSourceType = "UPLOAD" | "URL" | "MANUAL";

export type NotebookSource = {
  id: string;
  sourceType: NotebookDocumentSourceType;
  sourceUrl?: string | null;
  content?: string | null;
  sourceUrlText?: string | null;
  filePath?: string | null;
  filename?: string | null;
  createdAt?: Date;
  notebookId?: string;
};

type EditNotebookSourcesProps = {
  initialSources: NotebookSource[];
};

export function EditNotebookSources({
  initialSources,
}: EditNotebookSourcesProps) {
  const [sources, setSources] = useState<NotebookSource[]>(initialSources);
  const [isEditing] = useState(false);
  const [currentSource, setCurrentSource] = useState<"URL" | "TEXT" | "FILE">(
    "URL"
  );
  const [sourceValue, setSourceValue] = useState("");
  const [sourceError, setSourceError] = useState("");

  // Function to convert UI text/url/file to database sourceType
  const getSourceType = (
    type: "URL" | "TEXT" | "FILE"
  ): NotebookDocumentSourceType => {
    if (type === "URL") return "URL";
    if (type === "FILE") return "UPLOAD";
    return "MANUAL";
  };

  const addSource = () => {
    if (currentSource === "FILE") {
      // File sources are added via the FileUpload component
      return;
    }

    if (!sourceValue.trim()) {
      setSourceError("Source cannot be empty");
      return;
    }

    if (currentSource === "URL" && !isValidUrl(sourceValue)) {
      setSourceError("Please enter a valid URL");
      return;
    }

    // Create a temporary ID for the new source
    const newSource: NotebookSource = {
      id: `temp-${Date.now()}`,
      sourceType: getSourceType(currentSource),
      sourceUrl: currentSource === "URL" ? sourceValue : null,
      content: currentSource === "TEXT" ? sourceValue : null,
    };

    setSources([...sources, newSource]);
    setSourceValue("");
    setSourceError("");
  };

  const removeSource = (id: string) => {
    setSources(sources.filter((source) => source.id !== id));
  };

  const isValidUrl = (url: string) => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleFileUpload = (result: {
    filePath: string;
    filename: string;
    fileSize: number;
    fileType: string;
    publicUrl: string;
  }) => {
    const newSource: NotebookSource = {
      id: `temp-${Date.now()}`,
      sourceType: "UPLOAD",
      sourceUrl: result.publicUrl,
      filePath: result.filePath,
      filename: result.filename,
    };

    setSources([...sources, newSource]);
    setSourceError("");
  };

  const handleFileUploadError = (error: string) => {
    setSourceError(error);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-sm font-medium text-muted-foreground">Sources</h3>
      </div>

      {isEditing && (
        <div className="space-y-3 mb-4">
          {currentSource === "FILE" ? (
            <FileUpload
              onFileUpload={handleFileUpload}
              onError={handleFileUploadError}
              className="mb-4"
            />
          ) : (
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1">
                {currentSource === "URL" ? (
                  <Input
                    placeholder="Enter URL"
                    value={sourceValue}
                    onChange={(e) => setSourceValue(e.target.value)}
                  />
                ) : (
                  <Textarea
                    placeholder="Enter text source"
                    value={sourceValue}
                    onChange={(e) => setSourceValue(e.target.value)}
                    className="min-h-[120px] resize-y"
                  />
                )}
              </div>
              <div className="flex flex-row sm:flex-col gap-2">
                <Button type="button" onClick={addSource} className="flex-1">
                  Add
                </Button>
              </div>
            </div>
          )}

          <div className="flex flex-row gap-2">
            <Select
              value={currentSource}
              onValueChange={(value: string) => {
                setCurrentSource(value as "URL" | "TEXT" | "FILE");
                setSourceValue("");
                setSourceError("");
              }}
            >
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="URL">URL</SelectItem>
                <SelectItem value="TEXT">Text</SelectItem>
                <SelectItem value="FILE">File</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {sourceError && (
            <p className="text-destructive text-sm">{sourceError}</p>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 gap-2 max-h-[400px] overflow-y-auto pr-1">
        {sources.length === 0 ? (
          <p className="text-sm text-muted-foreground italic">
            No sources added yet
          </p>
        ) : (
          sources.map((source) => (
            <div
              key={source.id}
              className="flex items-start justify-between border rounded-lg p-3 bg-secondary/10"
            >
              <div className="flex items-start flex-1 overflow-hidden">
                {source.sourceType === "URL" ? (
                  <>
                    <LinkIcon className="h-4 w-4 mt-0.5 mr-2 text-blue-500 shrink-0" />
                    <div className="overflow-hidden flex-1">
                      <p className="text-xs font-medium text-blue-700 mb-1">URL</p>
                      <a
                        href={source.sourceUrl || "#"}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline break-all"
                      >
                        {source.sourceUrl}
                      </a>
                    </div>
                  </>
                ) : source.sourceType === "UPLOAD" ? (
                  <>
                    <Upload className="h-4 w-4 mt-0.5 mr-2 text-purple-500 shrink-0" />
                    <div className="overflow-hidden flex-1">
                      <p className="text-xs font-medium text-purple-700 mb-1">FILE</p>
                      <p className="text-sm font-medium text-purple-700">
                        {source.filename || "Uploaded file"}
                      </p>
                      {source.sourceUrl && (
                        <a
                          href={source.sourceUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-purple-600 hover:underline"
                        >
                          View file
                        </a>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    <FileText className="h-4 w-4 mt-0.5 mr-2 text-green-500 shrink-0" />
                    <div className="overflow-hidden flex-1">
                      <p className="text-xs font-medium text-green-700 mb-1">TEXT</p>
                      <p className="text-sm text-gray-700">
                        {source.content && source.content.length > 80
                          ? `${source.content.substring(0, 80)}...`
                          : source.content
                        }
                      </p>
                      {source.content && source.content.length > 80 && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {source.content.length} characters
                        </p>
                      )}
                    </div>
                  </>
                )}
              </div>
              {isEditing && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeSource(source.id)}
                  className="ml-2 shrink-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// Add default export for dynamic import
export default EditNotebookSources;
