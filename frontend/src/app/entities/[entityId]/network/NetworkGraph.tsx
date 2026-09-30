"use client";

import cytoscape from "cytoscape";
import { useEffect, useMemo, useRef } from "react";
import type { NetworkResponse } from "@/lib/types";

const colors: Record<string, string> = {
  Person: "#0369a1",
  Phone: "#0f766e",
  Account: "#7c3aed",
  Location: "#b45309",
  Vehicle: "#be123c",
  Organization: "#475569",
  Finding: "#b45309",
  Evidence: "#64748b",
  Event: "#0f766e",
};

type Props = {
  network: NetworkResponse;
  visibleTypes: string[];
  search: string;
  focusMode: boolean;
  fitRequest: number;
  selectedId: string | null;
  selectedEdgeId: string | null;
  onNodeSelect: (id: string) => void;
  onEdgeSelect: (id: string) => void;
};

export default function NetworkGraph({ network, visibleTypes, search, focusMode, fitRequest, selectedId, selectedEdgeId, onNodeSelect, onEdgeSelect }: Props) {
  const canvas = useRef<HTMLDivElement>(null);
  const graphRef = useRef<cytoscape.Core | null>(null);
  const callbacks = useRef({ onNodeSelect, onEdgeSelect });
  const distances = useMemo(() => getDistances(network), [network]);

  useEffect(() => { callbacks.current = { onNodeSelect, onEdgeSelect }; }, [onNodeSelect, onEdgeSelect]);

  useEffect(() => {
    if (!canvas.current) return;
    const graph = cytoscape({ container: canvas.current, style: [
      { selector: "node", style: { "background-color": "data(color)", label: "data(displayLabel)", color: "#183243", "font-size": "10px", "font-weight": "bold", "text-wrap": "ellipsis", "text-max-width": "110px", "text-valign": "bottom", "text-margin-y": 8, width: 28, height: 28, "border-width": 2, "border-color": "#ffffff" } },
      { selector: "node[root]", style: { width: 46, height: 46, "border-width": 5, "border-color": "#bae6fd", "font-size": "12px" } },
      { selector: "node[distance = 2]", style: { opacity: 0.72, "font-size": "8px" } },
      { selector: "node.selected", style: { "border-color": "#b4532a", "border-width": 5, opacity: 1 } },
      { selector: "node.filtered", style: { opacity: 0.12 } },
      { selector: "node.focus-hidden", style: { display: "none" } },
      { selector: "node.search-match", style: { "border-color": "#b4532a", "border-width": 4, opacity: 1 } },
      { selector: "edge", style: { width: 1.6, "line-color": "#cbd5e1", "target-arrow-color": "#cbd5e1", "target-arrow-shape": "triangle", "curve-style": "bezier", label: "data(displayLabel)", "font-size": "8px", color: "#64748b", opacity: 0.8 } },
      { selector: "edge.selected", style: { width: 3, "line-color": "#b4532a", "target-arrow-color": "#b4532a", label: "data(fullLabel)", opacity: 1 } },
      { selector: "edge.filtered", style: { opacity: 0.08 } },
    ], layout: { name: "preset" } });
    graphRef.current = graph;
    graph.on("tap", "node", (event) => callbacks.current.onNodeSelect(event.target.id()));
    graph.on("tap", "edge", (event) => callbacks.current.onEdgeSelect(event.target.id()));
    const resize = () => graph.resize();
    const observer = new ResizeObserver(resize);
    observer.observe(canvas.current);
    return () => { observer.disconnect(); graph.removeAllListeners(); graph.destroy(); graphRef.current = null; };
  }, []);

  useEffect(() => {
    const graph = graphRef.current;
    if (!graph) return;
    graph.elements().remove();
    graph.add([
      ...network.nodes.map((node) => ({ data: { id: node.id, label: node.label, displayLabel: node.id === network.root_entity_id || distances[node.id] === 1 ? node.label : "", entityType: node.entity_type, color: colors[node.entity_type] ?? "#64748b", root: node.id === network.root_entity_id, distance: distances[node.id] ?? 2 } })),
      ...network.edges.map((edge) => ({ data: { id: edge.id, source: edge.source, target: edge.target, displayLabel: "", fullLabel: edge.relationship } })),
    ]);
    graph.layout({ name: "concentric", animate: false, padding: 56, concentric: (node: cytoscape.NodeSingular) => node.id() === network.root_entity_id ? 10 : 1 / (distances[node.id()] ?? 2), levelWidth: () => 1, fit: true }).run();
  }, [network, distances]);

  useEffect(() => {
    const graph = graphRef.current;
    if (!graph) return;
    graph.nodes().removeClass("selected filtered focus-hidden search-match");
    graph.edges().removeClass("selected filtered");
    if (selectedId) graph.getElementById(selectedId).addClass("selected");
    if (selectedEdgeId) graph.getElementById(selectedEdgeId).addClass("selected");
    const query = search.trim().toLowerCase();
    graph.nodes().forEach((node) => {
      if (!visibleTypes.includes(node.data("entityType"))) node.addClass("filtered");
      if (query && `${node.data("label")} ${node.id()}`.toLowerCase().includes(query)) node.addClass("search-match");
      if (focusMode && selectedId && node.id() !== selectedId && !node.neighborhood().contains(graph.getElementById(selectedId))) node.addClass("focus-hidden");
    });
    graph.edges().forEach((edge) => {
      if (edge.source().hasClass("filtered") || edge.target().hasClass("filtered") || edge.source().hasClass("focus-hidden") || edge.target().hasClass("focus-hidden")) edge.addClass("filtered");
    });
  }, [visibleTypes, search, focusMode, selectedId, selectedEdgeId, network]);

  useEffect(() => { graphRef.current?.fit(undefined, 56); }, [fitRequest]);

  return <div ref={canvas} className="h-full min-h-105 w-full" aria-label="Interactive relationship network" role="img" />;
}

function getDistances(network: NetworkResponse): Record<string, number> {
  const distances: Record<string, number> = { [network.root_entity_id]: 0 };
  let frontier = [network.root_entity_id];
  for (let depth = 1; depth <= 2; depth += 1) {
    const next: string[] = [];
    network.edges.forEach((edge) => {
      const connected = frontier.includes(edge.source) ? edge.target : frontier.includes(edge.target) ? edge.source : null;
      if (connected && distances[connected] === undefined) { distances[connected] = depth; next.push(connected); }
    });
    frontier = next;
  }
  return distances;
}
