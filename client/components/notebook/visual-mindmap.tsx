"use client";

import React, { useMemo, useRef } from "react";
import { Mindmap } from "react-mindmap-visualiser";
import { Card, CardContent } from "@/components/ui/card";
import {
  BlockNodeStyle,
  TreeNode,
} from "react-mindmap-visualiser/build/helpers/getTreeLayout";

interface MindmapData {
  mindmap: Record<string, unknown>;
  title: string;
  description: string;
}

interface VisualMindmapProps {
  mindmapData: MindmapData;
}

export function VisualMindmap({ mindmapData }: VisualMindmapProps) {
  const mindmapRef = useRef<HTMLDivElement>(null);

  // Convert mindmap data to TreeNode format expected by react-mindmap-visualiser
  const treeData = useMemo(() => {
    // Add null/undefined checks
    if (!mindmapData || !mindmapData.mindmap) {
      console.warn("Invalid mindmap data:", mindmapData);
      return {
        id: "empty-root",
        text: "No mindmap data available",
        display: { block: true },
        nodes: [],
      };
    }

    const mindmap = mindmapData.mindmap;

    const getBlockStyleForLevel = (level: number): BlockNodeStyle => {
      switch (level % 5) {
        case 0:
          return "default";
        case 1:
          return "info";
        case 2:
          return "success";
        case 3:
          return "warn";
        case 4:
          return "danger";
        default:
          return "default";
      }
    };

    const processTreeNode = (node: TreeNode, level: number = 0): TreeNode => {
      const processedNode: TreeNode = {
        id: node.id || `node-${Math.random()}`,
        text: node.text || "Unknown",
        display: {
          block: true,
          blockStyle: getBlockStyleForLevel(level),
        },
        nodes: [],
      };

      if (node.nodes && Array.isArray(node.nodes) && node.nodes.length > 0) {
        processedNode.nodes = node.nodes.map((childNode: TreeNode) =>
          processTreeNode(childNode, level + 1)
        );
      }

      return processedNode;
    };

    console.log(
      "Processing mindmap data with block display and collapsed levels:",
      mindmap
    );

    const processedTree = processTreeNode(mindmap as unknown as TreeNode);
    console.log("Processed tree:", processedTree);
    return processedTree;
  }, [mindmapData]);

  return (
    <div className="space-y-4">
      <div className="text-center">
        <p className="text-muted-foreground">
          {mindmapData?.description ? "" : "Loading mindmap..."}
        </p>
      </div>

      <Card className="w-full">
        <CardContent className="p-0">
          <div
            ref={mindmapRef}
            className="w-full h-[700px] bg-linear-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 rounded-lg overflow-hidden"
          >
            <div className="w-full h-full p-4">
              <Mindmap json={treeData} />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}