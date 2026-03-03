
import { Component, useState, useEffect } from "@odoo/owl";

export class TodoApp extends Component {
    static template = "owl_todo.TodoApp";

    setup() {
        this.state = useState({
            newTask: "",
            tasks: [
                { id: 1, text: "Fix the 'this' error", isCompleted: true },
                { id: 2, text: "Enjoy Odoo 19", isCompleted: false },
            ],
        });

        useEffect(
            () => {
                console.log("Task Update detected:");
                console.table(this.state.tasks);
            },
            () => [this.state.tasks.length, ...this.state.tasks.map(t => t.isCompleted)]
        );
    }

    addTask = () => {
        const text = this.state.newTask.trim();
        if (text) {
            this.state.tasks.push({
                id: Date.now(),
                text: text,
                isCompleted: false,
            });
            this.state.newTask = "";
        }
    }

    toggleTask = (taskId) => {
        const task = this.state.tasks.find(t => t.id === taskId);
        if (task) {
            task.isCompleted = !task.isCompleted;
        }
    }

    deleteTask = (taskId) => {
        this.state.tasks = this.state.tasks.filter(t => t.id !== taskId);
    }
}