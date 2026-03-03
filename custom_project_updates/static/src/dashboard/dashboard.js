/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ProjectDashboard extends Component {
    static template = "custom_project_updates.ProjectDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.allTasks = [];

        this.state = useState({
            activeTab: "change",
            groups: {
                new: [],
                in_progress: [],
                done: [],
                due_soon: [],
                overdue: [],
                urgent: [],
            },
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    // Load Tasks
    async loadData() {
        // NOTE: Don't load the whole DB (keep the dashboard responsive).
        // Increase the limit if you need more.
        this.allTasks = await this.orm.searchRead(
            "project.task",
            [],
            ["name", "project_id", "date_deadline", "state", "stage_id", "is_urgent"],
            { limit: 500 }
        );

        this.filterTasks("");
    }

    // Tabs
    setTab(tab) {
        this.state.activeTab = tab;
    }

    getVisibleGroups() {
        if (this.state.activeTab === "change") {
            return ["new", "urgent"];
        }
        if (this.state.activeTab === "progress") {
            return ["in_progress", "due_soon", "overdue"];
        }
        return ["done"];
    }

    // Search
    onSearchInput(ev) {
        this.filterTasks(ev.target.value.toLowerCase());
    }

    // Group Logic
    filterTasks(term) {
        const today = new Date();
        const todayStr = today.toISOString().slice(0, 10);

        const soon = new Date();
        soon.setDate(today.getDate() + 3);
        const soonStr = soon.toISOString().slice(0, 10);

        const g = {
            new: [],
            in_progress: [],
            done: [],
            due_soon: [],
            overdue: [],
            urgent: [],
        };

        this.allTasks.forEach((task) => {
            if (term && !task.name.toLowerCase().includes(term)) return;

            const state = task.state || "";
            const stageName = task.stage_id ? String(task.stage_id[1] || "").toLowerCase() : "";
            const deadlineStr = task.date_deadline || null;

            // Try to classify by stage name first (more stable), fallback to "state" if your DB uses it.
            const isDone =
                stageName.includes("done") ||
                stageName.includes("closed") ||
                stageName.includes("complete") ||
                state === "1_done";

            const isNew =
                stageName.includes("new") ||
                stageName.includes("backlog") ||
                stageName.includes("to do") ||
                state === "04_waiting_normal" ||
                state === "02_changes_requested";

            const isInProgress =
                stageName.includes("progress") ||
                stageName.includes("in progress") ||
                stageName.includes("doing") ||
                state === "01_in_progress";

            if (isDone) {
                g.done.push(task);
            } else if (isNew) {
                g.new.push(task);
            } else if (isInProgress) {
                g.in_progress.push(task);
            } else {
                // If not classified, treat as in progress (better UX than "missing")
                g.in_progress.push(task);
            }

            if (task.is_urgent) {
                g.urgent.push(task);
            }

            if (!isDone && deadlineStr) {
                // date_deadline is YYYY-MM-DD; lexical compare works.
                if (deadlineStr < todayStr) g.overdue.push(task);
                else if (deadlineStr <= soonStr) g.due_soon.push(task);
            }
        });

        this.state.groups = g;
    }

    // Card → Form
    openTask(taskId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "project.task",
            res_id: taskId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    // Title → List
    openGroup(gKey) {
        const today = new Date().toISOString().slice(0, 10);

        const soon = new Date();
        soon.setDate(new Date().getDate() + 3);
        const soonStr = soon.toISOString().slice(0, 10);

        // Keep your original domains (for DBs using 'state'), but also add
        // a stage-name fallback for 'done' so it works in most databases.
        const domainMap = {
            new: [["state", "in", ["04_waiting_normal", "02_changes_requested"]]],
            in_progress: [["state", "=", "01_in_progress"]],
            done: ["|", ["state", "=", "1_done"], ["stage_id.name", "ilike", "done"]],
            urgent: [["is_urgent", "=", true]],
            overdue: [["date_deadline", "<", today], ["state", "!=", "1_done"]],
            due_soon: [["date_deadline", "<=", soonStr], ["state", "!=", "1_done"]],
        };

        this.action.doAction({
            type: "ir.actions.act_window",
            name: gKey.replace("_", " "),
            res_model: "project.task",
            views: [[false, "list"], [false, "form"]],
            domain: domainMap[gKey] || [],
            target: "current",
        });
    }
}

registry.category("actions").add("custom_project_updates.dashboard", ProjectDashboard);
