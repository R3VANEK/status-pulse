import type { Project } from "../types/project";

export const MOCK_PROJECTS: Project[] = [
  {
    id: "1",
    code: "PZ-01",
    name: "Aplikacja do zarządzania projektami",
    category: "Platforma zespołowa",
    status: "in_progress",
    team: ["JD", "AK", "MW"],
    tasksDone: 12,
    tasksTotal: 24,
  },
  {
    id: "2",
    code: "PZ-02",
    name: "System rezerwacji sal",
    category: "Aplikacja webowa",
    status: "in_progress",
    team: ["KN", "PB"],
    tasksDone: 8,
    tasksTotal: 18,
  },
  {
    id: "3",
    code: "PZ-03",
    name: "Portal koła naukowego",
    category: "Serwis informacyjny",
    status: "completed",
    team: ["AK", "MW"],
    tasksDone: 16,
    tasksTotal: 16,
  },
  {
    id: "4",
    code: "PZ-04",
    name: "Biblioteka online",
    category: "Projekt semestralny",
    status: "planned",
    team: ["JD", "KN"],
    tasksDone: 0,
    tasksTotal: 12,
  },
];

export const MOCK_PROJECTS_TOTAL = 12;
